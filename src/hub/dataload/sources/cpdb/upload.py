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
                "properties": {
                }
            }
        }
        for p_source in klass.PATHWAYS:
            mapping['pathway']['properties'][p_source] = {
                "dynamic": False,
                "properties": {
                    'id': {
                        "type": "text",
                        "copy_to": ["all"], 
                    },
                    'name': {
                        "type": "text",
                        "copy_to": ["all"],
                    }
                }
            }

            # now define the type for "copy_to" field above
            if p_source == "pharmgkb":
                # this would override the datasource's mapping
                continue
            mapping[p_source] = {
                "type": "text",
            }


        return mapping
