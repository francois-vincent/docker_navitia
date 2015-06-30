# encoding: utf-8

# Usage   : "py.test -s tests [-k test_case] [--nobuild] [--commit]" from within folder fabric_navitia
# Example : py.test -s -k test_deploy_two --commit
# you need to have your ssh's id_rsa.pub file in the same folder as the Dockerfile you use

from __future__ import unicode_literals, print_function
import os
import sys
import requests
import time
# sys.path.insert(1, os.path.abspath(os.path.join(__file__, '..', '..')))
sys.path[0] = os.path.abspath(os.path.join(__file__, '..', '..'))

from fabric import api

from docker_navitia.docker_navitia import ROOT, BuildDockerSimple, BuildDockerCompose, find_image, find_container

HOST_DATA_FOLDER = os.path.join(ROOT, 'data')
GUEST_DATA_FOLDER = '/srv/ed/data'
HOST_ZMQ_FOLDER = os.path.join(ROOT, 'zmq')
GUEST_ZMQ_FOLDER = api.env.kraken_basedir
DATA_FILE = os.path.join(ROOT, 'fixtures/data.zip')

if not os.path.isdir(HOST_DATA_FOLDER):
    os.mkdir(HOST_DATA_FOLDER)


class TestDeploy(object):

    def check_tyr(self, out):
        # TODO remove postgresql
        assert '/usr/lib/erlang/erts-6.2/bin/epmd -daemon' in out
        assert '/bin/sh /usr/sbin/rabbitmq-server' in out
        assert '/usr/lib/erlang/erts-6.2/bin/beam.smp -W w -K true -A30 -P 1048576 -- -root ' \
               '/usr/lib/erlang -progname erl -- -home /var/lib/rabbitmq -- ' \
               '-pa /usr/lib/rabbitmq/lib/rabbitmq_server-3.3.5/sbin/../ebin ' \
               '-noshell -noinput -s rabbit boot -sname r' in out
        assert 'inet_gethost 4' in out
        assert '/usr/bin/redis-server 127.0.0.1:6379' in out
        assert '/usr/bin/python -m celery worker -A tyr.tasks --events --pidfile=/tmp/tyr_worker.pid' in out
        assert '/usr/bin/python /usr/local/bin/celery --uid=www-data --gid=www-data ' \
               '--pidfile=/tmp/tyr_beat.pid -A tyr.tasks --detach beat' in out

    def check_jormun(self, out):
        assert '/usr/bin/redis-server 127.0.0.1:6379' in out
        assert '/usr/sbin/apache2 -k start' in out
        assert '(wsgi:jormungandr -k start' in out

    def check_db(self, out):
        assert '/usr/lib/postgresql/9.4/bin/postgres -D /var/lib/postgresql/9.4/main -c ' \
               'config_file=/etc/postgresql/9.4/main/postgresql.conf' in out
        assert 'postgres: checkpointer process' in out
        assert 'postgres: writer process' in out
        assert 'postgres: wal writer process' in out
        assert 'postgres: autovacuum launcher process' in out
        assert 'postgres: stats collector process' in out
        assert 'postgres: jormungandr jormungandr' in out

    def check_kraken(self, out):
        assert '/usr/sbin/apache2 -k start' in out
        assert '/usr/bin/redis-server 127.0.0.1:6379' in out
        assert '(wsgi:monitor-kra -k start' in out
        assert '/srv/kraken/paris/kraken' in out

    def check_processes(self, out):
        if isinstance(out, dict):
            self.check_db(out['ed'])
            self.check_tyr(out['tyr'])
            self.check_kraken(out['kraken'])
            self.check_jormun(out['jormun'])
        else:
            self.check_db(out)
            self.check_tyr(out)
            self.check_kraken(out)
            self.check_jormun(out)

    def deploy_simple(self):
        return BuildDockerSimple(volumes=[HOST_DATA_FOLDER + ':' + GUEST_DATA_FOLDER],
                                 ports=['8080:80'])

    def deploy_composed(self):
        return BuildDockerCompose().\
            add_image('ed', ports=[5432]).\
            add_image('tyr', links=['ed'], ports=[5672], volumes=[HOST_DATA_FOLDER + ':' + GUEST_DATA_FOLDER]).\
            add_image('kraken', links=['tyr', 'ed'],
                      volumes=[HOST_DATA_FOLDER + ':' + GUEST_DATA_FOLDER, HOST_ZMQ_FOLDER + ':' + GUEST_ZMQ_FOLDER]).\
            add_image('jormun', links=['ed'], ports=['8082:80'], volumes=[HOST_ZMQ_FOLDER + ':' + GUEST_ZMQ_FOLDER])

    def test_deploy_simple(self, commit):
        n = self.deploy_simple()
        assert n.image_name == 'navitia/debian8'
        assert n.container_name == 'navitia_simple'
        n.build()
        image = find_image(name=n.image_name)
        assert isinstance(image, dict)
        n.create()
        container = find_container(n.container_name)
        assert isinstance(container, dict)
        n.start()
        container = find_container(n.container_name, ignore_state=False)
        assert isinstance(container, dict)
        n.set_platform().execute()
        n.run('ps ax')
        self.check_processes(n.output)
        n.run('id')
        assert 'uid=1000(git) gid=1000(git) groups=1000(git),27(sudo),33(www-data)' in n.output
        assert requests.get('http://%s/navitia' % n.inspect()).status_code == 200
        assert requests.get('http://localhost:8080/navitia').status_code == 200
        n.stop().start().set_platform().execute('restart_all')
        n.run('ps ax')
        self.check_processes(n.output)
        assert requests.get('http://%s/navitia' % n.inspect()).status_code == 200
        n.run('chmod a+w /var/log/tyr/paris.log', sudo=True)
        n.run('rm -f %s/paris/data.nav.lz4' % GUEST_DATA_FOLDER)
        n.put(DATA_FILE, GUEST_DATA_FOLDER + '/paris', sudo=True)
        time.sleep(30)
        n.run('ls %s/paris' % GUEST_DATA_FOLDER)
        assert 'data.nav.lz4' in n.output
        if commit:
            n.commit()

    def test_deploy_composed(self, nobuild, nocreate, norestart):
        n = self.deploy_composed()
        assert n.images['tyr'].image_name == 'navitia/debian8_tyr'
        assert n.images['tyr'].container_name == 'navitia_composed_tyr'
        if norestart:
            n.stop().start()
            n.set_platform()
            n.run('ps ax')
        elif nocreate:
            n.stop().start()
            time.sleep(10)
            n.set_platform()
            n.execute('restart_all').run('service redis-server start', hosts=['kraken', 'jormun'], sudo=True)
            time.sleep(2)
            n.run('ps ax')
        elif nobuild:
            n.stop().rm().up()
            n.set_platform()
            n.execute().run('service redis-server start', hosts=['kraken', 'jormun'], sudo=True)
            time.sleep(2)
            n.run('ps ax')
        else:
            n.stop().rm().destroy()
            n.build()
            n.up().set_platform()
            n.execute().run('service redis-server start', hosts=['kraken', 'jormun'], sudo=True)
            time.sleep(2)
            n.run('ps ax')
        print(n.get_host())
        self.check_processes(n.output)
        assert requests.get('http://%s/navitia' % n.images['jormun'].inspect()).status_code == 200
