import os
import ConfigParser
from fabric.api import env, local, require

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


def load_configs_to_heroku():
    """
    """
    config = ConfigParser.ConfigParser()
    config.readfp(open(os.path.join(BASE_DIR, 'heroku.cfg')))
    local('heroku config:set %s=%s' % ('AWS_ACCESS_KEY_ID', config.get('Config', 'AWS_ACCESS_KEY_ID')))
    local('heroku config:set %s=%s' % ('AWS_SECRET_ACCESS_KEY', config.get('Config', 'AWS_SECRET_ACCESS_KEY')))
    local('heroku config:set %s=%s' % ('AWS_STATIC_STORAGE_BUCKET_NAME',
                                       config.get('Config', 'AWS_STATIC_STORAGE_BUCKET_NAME')))
    local('heroku config:set %s=%s' % ('SECRET_KEY', config.get('Config', 'SECRET_KEY')))
    local('heroku config:set %s=%s' % ('STATIC_URL', config.get('Config', 'STATIC_URL')))


