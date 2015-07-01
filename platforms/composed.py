# encoding: utf-8

from __future__ import unicode_literals, print_function

from fabric.api import env
from fabfile.instance import add_instance
from common import env_common


def composed(tyr, ed, kraken, jormun):
    env_common(tyr, ed, kraken, jormun)
    env.name = 'composed'
    env.TYR_WORKER_START_DELAY = 30
    env.APACHE_START_DELAY = 30

    env.rabbitmq_host = 'tyr'
    env.postgresql_database_host = 'ed'

    add_instance('default', 'default')
