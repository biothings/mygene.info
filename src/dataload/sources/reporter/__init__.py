from utils.dataload import merge_dict, value_convert

__metadata__ = {
    '__collection__': 'reporter',
    'structure': {'reporter': None},
}

reporter_modules = ['affy_reporter', 'affy_reporter2', 'gnf_reporter', 'pigatlas_reporter']
platform_li = []
for i, module in enumerate(reporter_modules):
    module = __import__('dataload.sources.reporter.'+module, fromlist=[module])
    reporter_modules[i] = module
    platform_li.extend(module.platform_li)


def load_genedoc(self=None):
    reporter_d = {}
    for module in reporter_modules:
        reporter_d.update(module.loaddata())
    platform_li = reporter_d.keys()
    genedoc_d = merge_dict([reporter_d[k] for k in platform_li], platform_li)
    fn = lambda value: {'reporter': value}
    genedoc_d = value_convert(genedoc_d, fn, traverse_list=False)
    return genedoc_d


def get_mapping(self=None):
    '''
    mapping = {
        "reporter":  {"dynamic" : False,
                      path": "just_name",
                      "properties" : {
                            "GNF1H": {
                               "type" : "string",
                                "analyzer": "string_lowercase",
                                "index_name": "reporter",
                            },
                            "GNF1M": {
                               "type" : "string",
                                "analyzer": "string_lowercase",
                                "index_name": "reporter",
                            },
                            ... ...
                      }
        }
    }
    '''

    platform_mapping = {
        "type": "string",
        "analyzer": "string_lowercase"
    }

    mapping = {
        "reporter": {
            "dynamic": False,
            #"path": "just_name",
            "properties": {}
        }
    }
    for platform in platform_li:
        mapping['reporter']['properties'][platform] = platform_mapping

    return mapping
