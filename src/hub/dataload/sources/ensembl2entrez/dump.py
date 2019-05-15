import os, sys, time, datetime

import biothings, config
biothings.config_for_app(config)

from config import DATA_ARCHIVE_ROOT
from biothings.hub.dataload.dumper import FilesystemDumper
from biothings.utils.hub_db import get_src_dump


class Ensembl2EntrezDumper(FilesystemDumper):

    SRC_NAME = "ensembl2entrez"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    FROM_SOURCE = {
            "name" : "ensembl",
            "files" : ["gene_ensembl__xref_entrezgene__dm.txt","gene_ensembl__gene__main.txt"]
            }
    TO_SOURCE = {
            "name" : "entrez",
            "files" : ["gene2ensembl.gz","gene_info.gz"]
            }
    SCHEDULE = "0 6 * * *"

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        # set during to_dump creation
        self.from_src = None
        self.to_src = None

    def set_release(self):
        assert self.from_src, "'from' source not defined"
        assert self.to_src, "'to' source not defined"
        self.release = "%s:%s" % (self.from_src["download"]["release"],self.to_src["download"]["release"])

    def create_todump_list(self, force=False):
        self.from_src = get_src_dump().find_one({"_id":self.__class__.FROM_SOURCE["name"]})
        self.to_src = get_src_dump().find_one({"_id":self.__class__.TO_SOURCE["name"]})
        from_folder = self.from_src.get("download",{}).get("data_folder")
        to_folder = self.to_src.get("download",{}).get("data_folder")
        assert from_folder, "Couldn't find folder for source %s (tried '%s')" % (self.from_src,from_folder)
        assert to_folder, "Couldn't find folder for source %s (tried '%s')" % (self.to_src,to_folder)

        self.set_release() # so we can generate new_data_folder
        for attr,folder in [("FROM_SOURCE",from_folder),("TO_SOURCE",to_folder)]:
            files = getattr(self.__class__,attr,{}).get("files")
            assert files, "No files specified in %s" % attr
            for one_file in files:
                remote_file = os.path.join(folder,one_file)
                assert os.path.exists(remote_file), "Remote file '%s' doesn't exist in %s" % (remote_file,attr)
                new_localfile = os.path.join(self.new_data_folder,one_file)
                current_localfile = os.path.join(self.current_data_folder,one_file)
                try:
                    remote_better = self.remote_is_better(remote_file,current_localfile)
                except FileNotFoundError:
                    # no local file, we want the remote
                    remote_better = True
                if force or current_localfile is None or remote_better:
                    self.to_dump.append({"remote":remote_file, "local":new_localfile})

