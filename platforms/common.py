# encoding: utf-8

from __future__ import unicode_literals, print_function
import os

from fabric.api import env

ROOT = os.path.dirname(os.path.abspath(__file__))
SSH_KEY_FILE = os.path.join(ROOT, 'unsecure_key')


def env_common(tyr, ed, kraken, jormun):
    env.key_filename = SSH_KEY_FILE
    env.use_ssh_config = True
    env.container = 'docker'
    env.use_syslog = False
    # just to verify /v1/coverage/$instance/status
    env.version = '0.101.2'

    env.roledefs = {
        'tyr':  [tyr],
        'tyr1': [tyr],
        'db':   [ed],
        'eng':  [kraken],
        'eng1': [kraken],
        'ws':   [jormun],
        'ws1':  [jormun],
    }

    env.excluded_instances = []
    env.manual_package_deploy = True
    env.setup_apache = True

    env.kraken_monitor_listen_port = 85
    env.jormungandr_save_stats = False
    env.jormungandr_is_public = True
    env.tyr_url = 'localhost:6000'

    env.tyr_backup_dir_template = '{base}/{instance}/backup/'
    env.tyr_source_dir_template = '{base}/data/{instance}'
    env.tyr_base_destination_dir = '/srv/ed/data/'

    env.jormungandr_url = jormun.split('@')[-1]
    env.kraken_monitor_base_url = kraken.split('@')[-1]

    # add your own custom configuration variables in file custom.py
    # e.g. env.email
    try:
        import custom
    except ImportError:
        pass
