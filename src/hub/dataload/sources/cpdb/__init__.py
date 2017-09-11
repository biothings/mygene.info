from .cpdb_base import load_cpdb, _download
import biothings.dataload.uploader as uploader


__metadata__ = {
    '__url_human__': 'http://cpdb.molgen.mpg.de/CPDB/getPathwayGenes?idtype=entrez-gene',
    '__url_mouse__': 'http://cpdb.molgen.mpg.de/MCPDB/getPathwayGenes?idtype=entrez-gene',
    '__url_yeast__': 'http://cpdb.molgen.mpg.de/YCPDB/getPathwayGenes?idtype=entrez-gene',
    # only import pathways from these sources
    'pathway_sources_included': [
        'biocarta',
        'humancyc',
        'kegg',
        'mousecyc',
        'netpath',
        'pharmgkb',
        'pid',
        'reactome',
        'smpdb',
        'wikipathways',
        'yeastcyc'
    ]
}


def download():
    _download(__metadata__)


class CPDBUploader(uploader.BaseSourceUploader):

    name = "cpdb"

    def load_data(self, data_folder):
        return load_cpdb(data_folder, __metadata__)

    def get_mapping(self):
        mapping = {
            "pathway": {
                "dynamic": False,
                #"path": "just_name",
                "properties": {
                }
            }
        }
        for p_source in __metadata__['pathway_sources_included']:
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
            mapping[p_source] = {
                "type": "string",
                "include_in_all": False
            }
    
        return mapping
