from .parser import load_cpdb
import biothings.hub.dataload.uploader as uploader


class CPDBUploader(uploader.BaseSourceUploader):

    name = "cpdb"
    PATHWAYS = ['biocarta','humancyc','kegg','mousecyc',
                'netpath','pharmgkb','pid','reactome',
                'smpdb','wikipathways','yeastcyc']

    def load_data(self, data_folder):
        return load_cpdb(data_folder, self.__class__.PATHWAYS)

    @classmethod
    def get_mapping(klass):
        mapping = {
            "pathway": {
                "dynamic": False,
                #"path": "just_name",
                "properties": {
                }
            }
        }
        for p_source in klass.PATHWAYS:
            mapping['pathway']['properties'][p_source] = {
                "dynamic": False,
                #"path": "just_name",
                "properties": {
                    'id': {
                        "type": "string",
                        "include_in_all": False,
                        #"index_name": p_source
                        "copy_to": p_source
                    },
                    'name': {
                        "type": "string",
                        "include_in_all": False,
                        #"index_name": p_source
                        "copy_to": p_source
                    }
                }
            }

            # now define the type for "copy_to" field above
            if p_source == "pharmgkb":
                # this would override the datasource's mapping
                continue
            mapping[p_source] = {
                "type": "string",
                "include_in_all": False
            }

        return mapping
