import os

import biothings
import biothings.hub.dataload.uploader as uploader
import timeout_decorator
from hub.dataload.nde import NDESourceUploader
from utils.pubtator import standardize_data
from utils.topic_category_helper import add_topic_category

class Biostudies_Uploader(uploader.ParallelizedSourceUploader):
    
    # name of the uploader
    name = "protein_parser"
    main_source = "refseq"

    storage_class = biothings.utils.storage.MergerStorage
    MAX_PARALLEL_UPLOAD = 5

    #TODO: needs to ensure that jobs take in a single file per time job
    def jobs(self):
        jobs = []
        # iterate over each directory in the download directory
        for file in os.listdir(self.data_folder):
            accno_file = os.path.join(self.data_folder, file)
            jobs.append((accno_file,))
        return jobs

    #TODO: needs futher review on the parsing function
    def load_data(self, input_file):
        try:
            docs = self.parse_files_with_timeout(input_file)
            for doc in docs:
                yield doc
        except TimeoutError:
            self.logger.info("Job timed out, TimeoutError in %s", input_file)
            # return an empty list as BasicStorage expects an iterable
            return []

    @classmethod
    def get_mapping(cls):
        return NDESourceUploader.get_mapping()