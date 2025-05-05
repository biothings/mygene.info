#!/usr/bin/env python

import logging
import os
from functools import partial

# shut some mouths...
logging.getLogger("elasticsearch").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("requests").setLevel(logging.ERROR)
logging.getLogger("botocore").setLevel(logging.ERROR)
logging.getLogger("boto3").setLevel(logging.ERROR)

import biothings
import config
from biothings.utils.version import set_versions

app_folder, _src = os.path.split(os.path.split(os.path.split(os.path.abspath(__file__))[0])[0])
set_versions(config, app_folder)
biothings.config_for_app(config)

import biothings.hub.databuild.builder as builder
import biothings.utils.mongo as mongo
from biothings.hub import HubServer
from biothings.hub.databuild.syncer import (
    SyncerManager,
    ThrottledESJsonDiffSelfContainedSyncer,
    ThrottledESJsonDiffSyncer,
)
from hub.databuild.builder import MyGeneDataBuilder
from hub.databuild.mapper import Ensembl2Entrez, EntrezRetired2Current


class MyGeneHubServer(HubServer):

    def configure_build_manager(self):
        retired2current = EntrezRetired2Current(convert_func=int, db_provider=mongo.get_src_db)
        ensembl2entrez = Ensembl2Entrez(db_provider=mongo.get_src_db, retired2current=retired2current)
        build_manager = builder.BuilderManager(
            builder_class=partial(MyGeneDataBuilder, mappers=[ensembl2entrez]),
            job_manager=self.managers["job_manager"],
        )
        build_manager.configure()
        build_manager.poll()
        self.managers["build_manager"] = build_manager
        self.logger.info("Using custom builder %s" % MyGeneDataBuilder)

    def configure_sync_manager(self):
        # prod
        sync_manager_prod = SyncerManager(job_manager=self.managers["job_manager"])
        sync_manager_prod.configure(
            klasses=[
                partial(ThrottledESJsonDiffSyncer, config.MAX_SYNC_WORKERS),
                partial(ThrottledESJsonDiffSelfContainedSyncer, config.MAX_SYNC_WORKERS),
            ]
        )
        self.managers["sync_manager"] = sync_manager_prod
        # test will access localhost ES, no need to throttle
        sync_manager_test = SyncerManager(job_manager=self.managers["job_manager"])
        sync_manager_test.configure()
        self.managers["sync_manager_test"] = sync_manager_test
        self.logger.info("Using custom syncer, prod(throttled): %s, test: %s" % (sync_manager_prod, sync_manager_test))

    def configure_commands(self):
        super().configure_commands()  # keep all originals...
        self.commands["es_sync_test"] = partial(
            self.managers["sync_manager_test"].sync,
            "es",
            target_backend=(
                config.INDEX_CONFIG["env"]["local"]["host"],
                config.INDEX_CONFIG["env"]["local"]["index"][0]["index"],
                config.INDEX_CONFIG["env"]["local"]["index"][0]["doc_type"],
            ),
        )
        self.commands["es_sync_prod"] = partial(
            self.managers["sync_manager"].sync,
            "es",
            target_backend=(
                config.INDEX_CONFIG["env"]["prod"]["host"],
                config.INDEX_CONFIG["env"]["prod"]["index"][0]["index"],
                config.INDEX_CONFIG["env"]["prod"]["index"][0]["doc_type"],
            ),
        )
        # self.commands["publish_diff_demo"] = partial(self.managers["diff_manager"].publish_diff,config.S3_APP_FOLDER + "-demo",
        #                                        s3_bucket=config.S3_DIFF_BUCKET + "-demo")
        # self.commands["snapshot_demo"] = partial(self.managers["index_manager"].snapshot,repository=config.SNAPSHOT_REPOSITORY + "-demo")
        # self.commands["publish_snapshot_demo"] = partial(self.managers["index_manager"].publish_snapshot,s3_folder=config.S3_APP_FOLDER + "-demo",
        #                                    repository=config.READONLY_SNAPSHOT_REPOSITORY)
        ## replace default
        # self.commands["publish_diff"] = partial(self.managers["diff_manager"].publish_diff,config.S3_APP_FOLDER)
        # self.commands["publish_snapshot"] = partial(self.managers["index_manager"].publish_snapshot,s3_folder=config.S3_APP_FOLDER)


import hub.dataload
from hub.datatransform.keylookup import MyGeneKeyLookup

# pass explicit list of datasources (no auto-discovery)
server = MyGeneHubServer(
    config.ACTIVE_DATASOURCES,
    name="MyGene.info",
    managers_custom_args={"dataplugin": {"keylookup": MyGeneKeyLookup}},
    api_config=False,
)

if __name__ == "__main__":
    server.start()
