import os
import ConfigParser
from fabric.api import env, local, require

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


def load_configs_to_heroku():
    """
    """
    config = ConfigParser.ConfigParser()
    config.readfp(open(os.path.join(BASE_DIR, 'heroku.cfg')))

    for s in config.sections():
        for v in config.items(s):
            local('heroku config:set %s=%s' % (v[0], v[1]))

