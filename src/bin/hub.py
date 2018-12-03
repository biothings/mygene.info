#!/usr/bin/env python

import os, logging
from functools import partial

import config, biothings
from biothings.utils.version import set_versions
app_folder,_src = os.path.split(os.path.split(os.path.split(os.path.abspath(__file__))[0])[0])
set_versions(config,app_folder)
biothings.config_for_app(config)

from biothings.hub import HubServer
import biothings.hub.databuild.builder as builder
import biothings.utils.mongo as mongo
from biothings.hub.databuild.syncer import SyncerManager, \
                                           ThrottledESJsonDiffSyncer, ThrottledESJsonDiffSelfContainedSyncer

from hub.databuild.mapper import EntrezRetired2Current, Ensembl2Entrez
from hub.databuild.builder import MyGeneDataBuilder


class MyGeneHubServer(HubServer):

    def configure_build_manager(self):
        retired2current = EntrezRetired2Current(convert_func=int,db_provider=mongo.get_src_db)
        ensembl2entrez = Ensembl2Entrez(db_provider=mongo.get_src_db,
        		retired2current=retired2current)
        build_manager = builder.BuilderManager(
                builder_class=partial(MyGeneDataBuilder,mappers=[ensembl2entrez]),
                job_manager=self.managers["job_manager"])
        build_manager.configure()
        self.managers["build_manager"] = build_manager
        self.logger.info("Using custom builder %s" % MyGeneDataBuilder)

    def configure_sync_manager(self):
        # prod
        sync_manager_prod = SyncerManager(job_manager=self.managers["job_manager"])
        sync_manager_prod.configure(klasses=[partial(ThrottledESJsonDiffSyncer,config.MAX_SYNC_WORKERS),
                                               partial(ThrottledESJsonDiffSelfContainedSyncer,config.MAX_SYNC_WORKERS)])
        self.managers["sync_manager"] = sync_manager_prod
        # test will access localhost ES, no need to throttle
        sync_manager_test = SyncerManager(job_manager=self.managers["job_manager"])
        sync_manager_test.configure()
        self.managers["sync_manager_test"] = sync_manager_test
        self.logger.info("Using custom syncer, prod(throttled): %s, test: %s" % (sync_manager_prod,sync_manager_test))

    def configure_commands(self):
        super().configure_commands() # keep all originals...
        self.commands["es_sync_test"] = partial(self.managers["sync_manager_test"].sync,"es",
                                           target_backend=(config.ES_CONFIG["env"]["test"]["host"],
                                                           config.ES_CONFIG["env"]["test"]["index"][0]["index"],
                                                           config.ES_CONFIG["env"]["test"]["index"][0]["doc_type"]))
        self.commands["es_sync_prod"] = partial(self.managers["sync_manager"].sync,"es",
                                           target_backend=(config.ES_CONFIG["env"]["prod"]["host"],
                                                           config.ES_CONFIG["env"]["prod"]["index"][0]["index"],
                                                           config.ES_CONFIG["env"]["prod"]["index"][0]["doc_type"]))
        self.commands["publish_diff_demo"] = partial(self.managers["diff_manager"].publish_diff,config.S3_APP_FOLDER + "-demo",
                                                s3_bucket=config.S3_DIFF_BUCKET + "-demo")
        self.commands["snapshot_demo"] = partial(self.managers["index_manager"].snapshot,repository=config.READONLY_SNAPSHOT_REPOSITORY + "-demo")
        self.commands["publish_snapshot_demo"] = partial(self.managers["index_manager"].publish_snapshot,s3_folder=config.S3_APP_FOLDER + "-demo",
                                            repository=config.READONLY_SNAPSHOT_REPOSITORY)
        # replace default
        self.commands["publish_diff"] = partial(self.managers["diff_manager"].publish_diff,config.S3_APP_FOLDER)
        self.commands["publish_snapshot"] = partial(self.managers["index_manager"].publish_snapshot,s3_folder=config.S3_APP_FOLDER)

    def before_start(self):
        self.logger.info("Scheduling builds")
        allspecies = partial(server.shell.launch,partial(server.managers["build_manager"].merge,"mygene_allspecies"))
        demo = partial(server.shell.launch,partial(server.managers["build_manager"].merge,"demo_allspecies"))
        server.managers["job_manager"].submit(allspecies,"0 2 * * 7")
        server.managers["job_manager"].submit(demo,"0 4 * * 7")

import hub.dataload
from hub.datatransform.keylookup import MyGeneKeyLookup
# pass explicit list of datasources (no auto-discovery)
server = MyGeneHubServer(hub.dataload.__sources_dict__,name="MyGene.info",
        managers_custom_args={"dataplugin" : {"keylookup" : MyGeneKeyLookup}})

if __name__ == "__main__":
    server.start()


