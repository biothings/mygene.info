import glob
import itertools
import json
import os
import os.path

import biothings

import config

biothings.config_for_app(config)

from biothings.hub.dataload.dumper import HTTPDumper
from biothings.utils.common import iter_n

from config import DATA_ARCHIVE_ROOT


class ChemblDumper(HTTPDumper):

    SRC_NAME = "chembl"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)

    SRC_VERSION_URL = "https://www.ebi.ac.uk/chembl/api/data/status.json"

    """
    As the code is written, we have:
    - 13,382 "target" json objects
    """
    SRC_DATA_URLS = {
        # Used to join with `mechanism` by `target_chembl_id`
        "target": "https://www.ebi.ac.uk/chembl/api/data/target.json",
    }

    # SCHEDULE = "0 12 * * *"
    SLEEP_BETWEEN_DOWNLOAD = 0.1
    MAX_PARALLEL_DUMP = 5

    # number of documents in each download job, i.e. number of documents in each .part* file
    TO_DUMP_DOWNLOAD_SIZE = 1000
    # number of .part* files to be merged together after download
    POST_DUMP_MERGE_SIZE = 100

    def get_total_count_of_documents(self, src_data_name):
        """
        Get the total count of documents from the first page of the url specified by `src_data_name`.
        `total_count` is a member of the `page_meta` member of the root json object.

        Args:
            src_data_name (str): must be a key to self.__class__.SRC_DATA_URLS

        Returns:
            int: the total count of documents
        """
        if src_data_name not in self.__class__.SRC_DATA_URLS:
            raise KeyError(
                "Cannot recognize src_data_name={}. Must be one of {{{}}}".format(
                    src_data_name, ", ".join(self.__class__.SRC_DATA_URLS.keys())
                )
            )

        data = self.load_json_from_file(self.__class__.SRC_DATA_URLS[src_data_name])
        return data["page_meta"]["total_count"]

    def load_json_from_file(self, file) -> dict:
        """
        Read the content of `file` and return the json object

        Args:
            file (str): could either be an URL ("remotefile") or a path to a local text file ("localfile")

        Returns:
            object: the json object read from the `file`
        """

        """
        Note that:

        - `json.loads(string)` deserializes string
        - `json.load(file)` deserializes a file object
        """
        if file.startswith("http://") or file.startswith("https://"):  # file is an URL
            data = json.loads(self.client.get(file).text)
        else:  # file is a local path
            data = json.load(open(file))

        return data

    def remote_is_better(self, remotefile, localfile):
        remote_data = self.load_json_from_file(remotefile)
        assert "chembl_db_version" in remote_data
        assert remote_data["status"] == "UP"  # API is working correctly
        self.release = remote_data["chembl_db_version"]

        if localfile is None:
            # ok we have the release, we can't compare further so we need to download
            return True

        local_data = self.load_json_from_file(localfile)
        self.logger.info(
            "ChEMBL DB version: remote=={}, local=={}".format(
                remote_data["chembl_db_version"], local_data["chembl_db_version"]
            )
        )

        # comparing strings should work since it's formatted as "ChEMBL_xxx"
        if remote_data["chembl_db_version"] > local_data["chembl_db_version"]:
            return True
        else:
            return False

    def create_todump_list(self, force=False, **kwargs):
        version_filename = os.path.basename(self.__class__.SRC_VERSION_URL)
        try:
            current_localfile = os.path.join(self.current_data_folder, version_filename)
            if not os.path.exists(current_localfile):
                current_localfile = None
        except TypeError:
            # current data folder doesn't even exist
            current_localfile = None

        remote_better = self.remote_is_better(
            self.__class__.SRC_VERSION_URL, current_localfile
        )
        self.logger.info(
            "ChEMBL Dump: force=={}, current_localfile=={}, remote_better=={}".format(
                force, current_localfile, remote_better
            )
        )

        if force or current_localfile is None or remote_better:
            new_localfile = os.path.join(self.new_data_folder, version_filename)
            self.to_dump.append(
                {"remote": self.__class__.SRC_VERSION_URL, "local": new_localfile}
            )

            """
            Now we need to scroll the API endpoints. Let's get the total number of records
            and generate URLs for each call to parallelize the downloads for each type of source data,
            i.e. "molecule", "mechanism", "drug_indication", "target" and "binding_site".

            The partition size is set to 1000 json objects (represented by `TO_DUMP_DOWNLOAD_SIZE`).

            E.g. suppose for "molecule" data we have a `total_count` of 2500 json objects, and then we'll have,
            in the process of iteration:

            - (part_index, part_start) = (0, 0)
            - (part_index, part_start) = (1, 1000)
            - (part_index, part_start) = (2, 2000)

            Therefore we would download 3 files, i.e. "molecule.part0", "molecule.part1", and "molecule.part2".
            """
            part_size = self.__class__.TO_DUMP_DOWNLOAD_SIZE
            for src_data_name in self.__class__.SRC_DATA_URLS:
                total_count = self.get_total_count_of_documents(src_data_name)
                for part_index, part_start in enumerate(
                    range(0, total_count, part_size)
                ):
                    remote = (
                        self.__class__.SRC_DATA_URLS[src_data_name]
                        + "?limit="
                        + str(part_size)
                        + "&offset="
                        + str(part_start)
                    )
                    local = os.path.join(
                        self.new_data_folder,
                        "{}.part{}".format(src_data_name, part_index),
                    )
                    self.to_dump.append({"remote": remote, "local": local})

    def post_dump(self, *args, **kwargs):
        """
        In the post-dump phase, for each type of source data, we merge each chunk of 100 .part* files
        into one .*.json file. (This way we won't have a small number of huge files nor a pile of small files.)

        E.g. as the code is written, we have 1,961,462 "molecule" json objects.
        Therefore we would download 1,962 files, i.e. "molecule.part0", ..., "molecule.part1961".
        For each chunk of 100 such files, e.g. "molecule.part0", ..., "molecule.part99", we merge them into one
        json file, e.g. "molecule.100.json".

        We'll also remove metadata (useless now)
        """
        self.logger.info("Merging JSON documents in '%s'" % self.new_data_folder)

        chunk_size = self.__class__.POST_DUMP_MERGE_SIZE
        for src_data_name in self.__class__.SRC_DATA_URLS:
            part_files = glob.iglob(
                os.path.join(self.new_data_folder, "{}.part*".format(src_data_name))
            )
            for chunk, cnt in iter_n(part_files, chunk_size, with_cnt=True):
                outfile = os.path.join(
                    self.new_data_folder, "{}.{}.json".format(src_data_name, cnt)
                )

                """
                For each "molecule" json object, we only fetch the value associated with the "molecules" key.
                This rule also applies to "mechanism", "drug_indication", "target" and "binding_site"
                json objects.
                """
                data_key = src_data_name + "s"
                merged_value = itertools.chain.from_iterable(
                    self.load_json_from_file(f)[data_key] for f in chunk
                )
                merged_data = {data_key: list(merged_value)}

                json.dump(merged_data, open(outfile, "w"))
                self.logger.info("Merged %s %s files" % (src_data_name, cnt))

            # now we can delete the part files
            self.logger.info("Deleting part files")
            part_files = glob.iglob(
                os.path.join(self.new_data_folder, "{}.part*".format(src_data_name))
            )
            for f in part_files:
                os.remove(f)

        self.logger.info("Post-dump merge done")
