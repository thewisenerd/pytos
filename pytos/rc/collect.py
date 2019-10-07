from pytos.db.base import Database
from pytos.models.configuration import Configuration
from pytos.models.context import Context
from pytos.rc.init import InitializeLibrary


def collect():
    return {
        'init': InitializeLibrary()
    }


def initialize_context(cfg_file) -> [Context, int]:
    config = Configuration(cfg_file)
    ret = config.validate()
    if ret != 0:
        return None, ret

    db = Database(config.db)
    return Context(config, db), 0
