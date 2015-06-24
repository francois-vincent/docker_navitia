# encoding: utf-8

from __future__ import unicode_literals, print_function
import os

from fabric.api import env

ROOT = os.path.dirname(os.path.abspath(__file__))
SSH_KEY_FILE = os.path.join(ROOT, 'unsecure_key')

SMTP_HOST = 'smtp.canaltp.local'
EMAIL_AUTHOR = (u'RO-noreply', u'Déploiement')
EMAIL_START_SUBJECT = u"Début de livraison Navitia 2 v{version} sur la plateforme {target}"
EMAIL_START_MESSAGE = u"Une livraison de la nouvelle version de Navitia 2 démarre sur la plateforme %s" \
                      u"\nVous pourriez être impacté."
EMAIL_FINISHED_SUBJECT = u"Fin de livraison Navitia 2 v{version} sur la plateforme {target}"
EMAIL_FINISHED_MESSAGE = u"Nouvelle version Navitia 2 déployée sur %s.\n\o/ Merci de votre patience !"


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

    env.emails = {
        'allow_start': True,
        'allow_finished': True,
        'server': SMTP_HOST,
        'author': EMAIL_AUTHOR,
        'start_sub': EMAIL_START_SUBJECT,
        'start_mes': EMAIL_START_MESSAGE,
        'end_sub': EMAIL_FINISHED_SUBJECT,
        'end_mes': EMAIL_FINISHED_MESSAGE,
        'to': 'francois.vincent@canaltp.fr',
        'cc': None
    }
    env.excluded_instances = []
    env.nb_thread_for_bina = 2
    env.dry_run = False
    env.use_protobuf_cpp = False
    env.setup_apache = True
    env.manual_package_deploy = True

    env.jormungandr_port = 80
    env.jormungandr_listen_port = 80
    env.kraken_monitor_port = 80
    env.kraken_monitor_listen_port = 85
    env.jormungandr_save_stats = False
    env.jormungandr_is_public = True
    env.tyr_url = 'localhost:6000'
    env.kill_ghost_tyr_worker = True

    env.tyr_backup_dir_template = '{base}/{instance}/backup/'
    env.tyr_source_dir_template = '{base}/data/{instance}'
    env.tyr_base_destination_dir = '/srv/ed/data/'
    env.kraken_database_file = '{base_dest}/{instance}/data.nav.lz4'

    env.jormungandr_url = jormun.split('@')[-1]
    env.kraken_monitor_base_url = kraken.split('@')[-1]
