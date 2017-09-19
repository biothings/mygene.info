from biothings.utils.dataload import merge_dict, value_convert
import biothings.hub.dataload.uploader as uploader


reporter_modules = ['affy_reporter', 'affy_reporter2', 'gnf_reporter', 'pigatlas_reporter']
platform_li = []
for i, module in enumerate(reporter_modules):
    module = __import__('hub.dataload.sources.reporter.' + module, fromlist=[module])
    reporter_modules[i] = module
    platform_li.extend(module.platform_li)


class ReporterUploader(uploader.DummySourceUploader):

    name = "reporter"

    def load_data(self, data_folder):
        raise Exception("Collection-only resource, no more dataload")
        reporter_d = {}
        for module in reporter_modules:
            reporter_d.update(module.loaddata(data_folder))
        platform_li = reporter_d.keys()
        genedoc_d = merge_dict([reporter_d[k] for k in platform_li], platform_li)
        fn = lambda value: {'reporter': value}
        genedoc_d = value_convert(genedoc_d, fn, traverse_list=False)
        return genedoc_d

    @classmethod
    def get_mapping(klass):
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
