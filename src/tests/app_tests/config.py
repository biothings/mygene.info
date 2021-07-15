
import importlib.util as _imp_util
from os.path import dirname, join, pardir
import sys


# find the path of the config file
_cfg_path = join(dirname(__file__), pardir, pardir)
sys.path.append(_cfg_path)
_cfg_path = join(_cfg_path, "config_web.py")

# load config file using path
_spec = _imp_util.spec_from_file_location("parent_config", _cfg_path)
_config = _imp_util.module_from_spec(_spec)
_spec.loader.exec_module(_config)

# put the config variables into the module namespace
for _k, _v in _config.__dict__.items():
    if not _k.startswith('_'):
        globals()[_k] = _v

# override default
ES_HOST = 'localhost:9200'
ES_INDEX = 'mygene_test'
