
import biothings.databuild.backend as btbackend
from biothings.utils.common import get_timestamp, get_random_string

class MyGeneTargetDocMongoBackend(btbackend.TargetDocMongoBackend):

    def generate_target_name(self,build_config_name):
        return 'genedoc_{}_{}_{}'.format(build_config_name,
                    get_timestamp(), get_random_string()).lower()


