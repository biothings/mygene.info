#!/usr/bin/env python

import asyncio, asyncssh, sys

import concurrent.futures
import multiprocessing_on_dill
concurrent.futures.process.multiprocessing = multiprocessing_on_dill

from functools import partial
from collections import OrderedDict

import config, biothings
biothings.config_for_app(config)

import logging
# shut some mouths...
logging.getLogger("elasticsearch").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("requests").setLevel(logging.ERROR)
logging.getLogger("boto").setLevel(logging.ERROR)

logging.info("Hub DB backend: %s" % biothings.config.HUB_DB_BACKEND)
logging.info("Hub database: %s" % biothings.config.DATA_HUB_DB_DATABASE)

from biothings.utils.manager import JobManager
loop = asyncio.get_event_loop()
process_queue = concurrent.futures.ProcessPoolExecutor(max_workers=config.HUB_MAX_WORKERS)
thread_queue = concurrent.futures.ThreadPoolExecutor()
loop.set_default_executor(process_queue)
job_manager = JobManager(loop,num_workers=config.HUB_MAX_WORKERS,
                      max_memory_usage=config.HUB_MAX_MEM_USAGE)

import hub.dataload
import biothings.hub.dataload.uploader as uploader
import biothings.hub.dataload.dumper as dumper
import biothings.hub.databuild.builder as builder
import biothings.hub.databuild.differ as differ
import biothings.hub.databuild.syncer as syncer
import biothings.hub.dataindex.indexer as indexer
from hub.databuild.builder import MyGeneDataBuilder
from hub.databuild.mapper import EntrezRetired2Current, Ensembl2Entrez
from hub.dataindex.indexer import GeneIndexer
import biothings.utils.mongo as mongo

# will check every 10 seconds for sources to upload
upload_manager = uploader.UploaderManager(poll_schedule = '* * * * * */10', job_manager=job_manager)
upload_manager.register_sources(hub.dataload.__sources_dict__)
upload_manager.poll('upload',lambda doc: upload_manager.upload_src(doc["_id"]))

dmanager = dumper.DumperManager(job_manager=job_manager)
dmanager.register_sources(hub.dataload.__sources_dict__)
dmanager.schedule_all()

retired2current = EntrezRetired2Current(convert_func=int,db_provider=mongo.get_src_db)
ensembl2entrez = Ensembl2Entrez(db_provider=mongo.get_src_db,
		retired2current=retired2current)
build_manager = builder.BuilderManager(
        builder_class=partial(MyGeneDataBuilder,mappers=[ensembl2entrez]),
        job_manager=job_manager)
build_manager.configure()

differ_manager = differ.DifferManager(job_manager=job_manager,
        poll_schedule="* * * * * */10")
differ_manager.configure()
differ_manager.poll("diff",lambda doc: differ_manager.diff("jsondiff-selfcontained",old=None,new=doc["_id"]))
differ_manager.poll("release_note",lambda doc: differ_manager.release_note(old=None,new=doc["_id"]))

# test will access localhost ES, no need to throttle
syncer_manager_test = syncer.SyncerManager(job_manager=job_manager)
syncer_manager_test.configure()
# prod needs to be throttled
from biothings.hub.databuild.syncer import ThrottledESJsonDiffSyncer, ThrottledESJsonDiffSelfContainedSyncer
syncer_manager_prod = syncer.SyncerManager(job_manager=job_manager)
syncer_manager_prod.configure(klasses=[partial(ThrottledESJsonDiffSyncer,config.MAX_SYNC_WORKERS),
                                       partial(ThrottledESJsonDiffSelfContainedSyncer,config.MAX_SYNC_WORKERS)])

index_manager = indexer.IndexerManager(job_manager=job_manager)
pindexer = partial(GeneIndexer,es_host=config.ES_HOST)
index_manager.configure([{"default" : pindexer}])

from biothings.utils.hub import schedule, pending, done, _and

def trigger_merge(build_name):
    @asyncio.coroutine
    def do():
        build_manager.merge(build_name)
    return asyncio.ensure_future(do())
mygene = partial(build_manager.merge,"mygene")
allspecies = partial(build_manager.merge,"mygene_allspecies")
demo = partial(build_manager.merge,"demo_allspecies")
job_manager.submit(partial(_and,mygene,allspecies,demo),"0 2 * * 7")


COMMANDS = OrderedDict()
# dump commands
COMMANDS["dump"] = dmanager.dump_src
COMMANDS["dump_all"] = dmanager.dump_all
# upload commands
COMMANDS["upload"] = upload_manager.upload_src
COMMANDS["upload_all"] = upload_manager.upload_all
# building/merging
COMMANDS["whatsnew"] = build_manager.whatsnew
COMMANDS["lsmerge"] = build_manager.list_merge
COMMANDS["merge"] = build_manager.merge
COMMANDS["es_sync_gene_test"] = partial(syncer_manager_test.sync,"es",target_backend=config.ES_TEST_GENE)
COMMANDS["es_sync_gene_allspecies_test"] = partial(syncer_manager_test.sync,"es",target_backend=config.ES_TEST_GENE_ALLSPECIES)
COMMANDS["es_sync_gene_prod"] = partial(syncer_manager_prod.sync,"es",target_backend=config.ES_PROD_GENE)
COMMANDS["es_sync_gene_allspecies_prod"] = partial(syncer_manager_prod.sync,"es",target_backend=config.ES_PROD_GENE_ALLSPECIES)
# TODO: replace above with these ones when switching only one allspecies index 
##COMMANDS["es_sync_gene_test"] = partial(syncer_manager_test.sync,"es",target_backend=config.ES_TEST_GENE)
#COMMANDS["es_sync_test"] = partial(syncer_manager_test.sync_test,"es",target_backend=config.ES_TEST_GENE_ALLSPECIES)
##COMMANDS["es_sync_gene_prod"] = partial(syncer_manager_prod.sync,"es",target_backend=config.ES_PROD_GENE)
#COMMANDS["es_sync_prod"] = partial(syncer_manager_prod.sync,"es",target_backend=config.ES_PROD_GENE_ALLSPECIES)
COMMANDS["es_prod"] = {"gene":config.ES_PROD_GENE,"gene_allspecies":config.ES_PROD_GENE_ALLSPECIES}
COMMANDS["es_test"] = {"gene":config.ES_TEST_GENE,"gene_allspecies":config.ES_TEST_GENE_ALLSPECIES}
# diff
COMMANDS["diff"] = partial(differ_manager.diff,"jsondiff-selfcontained")
COMMANDS["report"] = differ_manager.diff_report
COMMANDS["release_note"] = differ_manager.release_note
COMMANDS["publish_diff"] = partial(differ_manager.publish_diff,config.S3_APP_FOLDER)
COMMANDS["publish_diff_demo"] = partial(differ_manager.publish_diff,config.S3_APP_FOLDER + "-demo",
                                        s3_bucket=config.S3_DIFF_BUCKET + "-demo")
# indexing j
COMMANDS["index"] = partial(index_manager.index,"default")
COMMANDS["snapshot"] = index_manager.snapshot
#COMMANDS["publish_snapshot_gene"] = partial(index_manager.publish_snapshot,config.S3_APP_FOLDER % "gene")
COMMANDS["publish_snapshot"] = partial(index_manager.publish_snapshot,config.S3_APP_FOLDER)
COMMANDS["publish_snapshot_demo"] = partial(index_manager.publish_snapshot,config.S3_APP_FOLDER + "-demo")

# admin/advanced
EXTRA_NS = {
        "dm" : dmanager,
        "um" : upload_manager,
        "bm" : build_manager,
        "dim" : differ_manager,
        "smt" : syncer_manager_test,
        "smp" : syncer_manager_prod,
        "im" : index_manager,
        "jm" : job_manager,
        "mongo_sync" : partial(syncer_manager_test.sync,"mongo"),
        "es_sync_test" : partial(syncer_manager_test.sync,"es"),
        "es_sync_prod" : partial(syncer_manager_prod.sync,"es"),
        "loop" : loop,
        "pqueue" : process_queue,
        "tqueue" : thread_queue,
        "g": globals(),
        "sch" : partial(schedule,loop),
        "top" : job_manager.top,
        "pending" : pending,
        "done" : done,
        }

from biothings.utils.hub import start_server

server = start_server(loop,"MyGene hub",passwords=config.HUB_PASSWD,
    port=config.HUB_SSH_PORT,commands=COMMANDS,extra_ns=EXTRA_NS)

try:
    loop.run_until_complete(server)
except (OSError, asyncssh.Error) as exc:
    sys.exit('Error starting server: ' + str(exc))

loop.run_forever()

