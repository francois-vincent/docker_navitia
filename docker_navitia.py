# encoding: utf-8

from __future__ import unicode_literals, print_function
import glob
from importlib import import_module
from jinja2 import Environment, FileSystemLoader
import os
import shutil
import sys

import docker
from fabric import api, context_managers, operations, tasks

# generally, fabric-navitia is a brother folder, if not, set environment variable PYTHONPATH
sys.path.insert(1, os.path.abspath(os.path.join(__file__, '..', '..', 'fabric_navitia')))
import fabfile

ROOT = os.path.dirname(os.path.abspath(__file__))
DOCKER_ROOT = os.path.join(ROOT, 'docker')
SSH_KEY_FILE = os.path.join(ROOT, 'platforms', 'unsecure_key.pub')
PLATFORMS = 'platforms'

# version='auto' is better if you wish to use different docker API versions
docker_client = docker.Client(base_url='unix://var/run/docker.sock', version='auto')

IMAGE_PREFIX = 'navitia/'
CONTAINER_PREFIX = 'navitia_'


def set_prefixes(prefix):
    global IMAGE_PREFIX, CONTAINER_PREFIX
    IMAGE_PREFIX = prefix + '/'
    CONTAINER_PREFIX = prefix + '_'


def wait(iterable, verbose=False):
    for line in iterable:
        if verbose:
            print(line, end='')
        if line.startswith(b'{"errorDetail'):
            raise RuntimeError("Build failed @" + line)


def resolve_module(module, root):
    if '.' in module:
        return module
    else:
        return root + '.' + module


def find_image(id=None, name=None):
    if id:
        for img in docker_client.images():
            if id == img['Id']:
                return img
    elif name:
        for img in docker_client.images():
            for t in img['RepoTags']:
                if t.split(':')[0] == name:
                    return img


def find_container(container=None, image=None, ignore_state=True):
    if container:
        for cont in docker_client.containers(all=ignore_state):
            if not image or cont['Image'].split(':')[0] == image:
                for name in cont['Names']:
                    if name[1:] == container:
                        return cont
    elif image:
        for cont in docker_client.containers(all=ignore_state):
            if cont['Image'].split(':')[0] == image:
                return cont


class DockerImageMixin(object):

    def set_path(self, path):
        if os.path.isdir(path) and os.access(os.path.join(path, 'Dockerfile'), os.R_OK):
            self.dockerpath = path
            shutil.copy(SSH_KEY_FILE, path)
        else:
            raise RuntimeError("Invalid path or missing Dockerfile in '%s'" % path)

    def process_options(self, **options):
        kwargs = {}
        self.user = options.get('user', 'navitia')
        volumes = options.get('volumes')
        self.volumes = []
        if volumes:
            binds = {}
            for vol in volumes:
                host, guest = vol.split(':', 1)
                # default mode is 'rw', you can specify 'ro' instead
                if ':' in guest:
                    guest, mode = guest.split(':')
                else:
                    mode = 'rw'
                host = os.path.expanduser(host)
                self.volumes.append(guest)
                binds[host] = {'bind': guest, 'mode': mode}
            kwargs['binds'] = binds
        ports = options.get('ports')
        self.ports = []
        if ports:
            port_bindings = {}
            for port in ports:
                if isinstance(port, basestring):
                    if ':' in port:
                        # TODO does not accept format host_ip:host_port:guest_port yet
                        host, guest = port.rsplit(':', 1)
                        guest = int(guest)
                        port_bindings[guest] = int(host)
                        self.ports.append(guest)
                    elif '-' in port:
                        start, end = port.split('-')
                        for p in xrange(int(start), int(end) + 1):
                            port_bindings[p] = None
                            self.ports.append(p)
                    else:
                        port = int(port)
                        port_bindings[port] = None
                        self.ports.append(port)
                else:
                    port_bindings[port] = None
                    self.ports.append(port)
            self.ports.sort()
            kwargs['port_bindings'] = port_bindings
        self.host_config = docker.utils.create_host_config(**kwargs)

    def inspect(self, field='NetworkSettings.IPAddress'):
        config = docker_client.inspect_container(container=self.container)
        if field:
            for x in field.split('.'):
                if x:
                    config = config.get(x)
        return config

    def get_host(self):
        return self.user + '@' + self.inspect()

    def set_container(self):
        container = find_container(container=self.container_name)
        self.container = container['Id'] if container else None
        return self

    def build(self):
        print('Building {} from {}/Dockerfile'.format(self.image_name, self.dockerpath))
        wait(docker_client.build(path=self.dockerpath, tag=self.image_name, rm=True))
        return self

    def destroy(self, image_name=None):
        image_name = image_name or self.image_name
        print("Removing image '{}'".format(image_name))
        try:
            docker_client.remove_image(image=image_name)
        except docker.errors.APIError:
            print("  image not found")
        return self

    def create(self):
        kwargs = dict(image=self.image_name, name=self.container_name, hostname=self.host)
        if self.volumes or self.ports:
            kwargs['host_config'] = self.host_config
            if self.ports:
                kwargs['ports'] = self.ports
            if self.volumes:
                kwargs['volumes'] = self.volumes
        try:
            self.container = docker_client.create_container(**kwargs).get('Id')
        except docker.errors.APIError:
            docker_client.pull(self.image_name)
            self.container = docker_client.create_container(**kwargs).get('Id')
        return self

    def start(self):
        if not self.container:
            self.set_container()
        docker_client.start(container=self.container)
        self.set_platform()
        return self

    def stop(self):
        if not self.container:
            self.set_container()
        if self.container:
            docker_client.stop(container=self.container)
        else:
            print("Container {} not found, stop skipped".format(self.container_name))
        return self

    def remove(self):
        if self.container:
            docker_client.remove_container(container=self.container)
            self.container = None
        return self

    def commit(self, image_name=None, tag=None):
        if not image_name:
            image_name = self.image_name + '_' + self.short_container_name
        if tag:
            try:
                tag = glob.glob('navitia-kraken_*.deb')[0].split('_')[1]
            except Exception:
                tag = 'latest'
            docker_client.commit(self.container_name, image_name, tag)
        else:
            docker_client.commit(self.container_name, image_name)
        return self

    def run(self, cmd, sudo=False):
        launch = operations.sudo if sudo else operations.run
        with context_managers.settings(
                context_managers.hide('stdout'),
                host_string=self.get_host()):
            self.output = launch(cmd)
        return self

    def put(self, source, dest, sudo=False):
        with context_managers.settings(host_string=self.get_host()):
            operations.put(source, dest, use_sudo=sudo)
        return self

    def clean_image(self):
        self.run("apt-get clean && rm -rf /var/lib/apt/lists/* /var/tmp/*", sudo=True)
        return self


class FabricDeployMixin(object):

    def set_platform(self):
        module = import_module(resolve_module(self.platform, PLATFORMS))
        api.env.distrib = self.distrib
        host_ref = self.get_host()
        if isinstance(host_ref, dict):
            getattr(module, self.platform)(**host_ref)
        else:
            getattr(module, self.platform)(host_ref)
        return self

    def execute(self, cmd='deploy_from_scratch', *args, **kwargs):
        """
        Executes a fabric-navitia command
        :param cmd: the fabric command
        :param *args are passed to api.execute
        :param **kwargs are passed to api.execute, except 'let' which is
               passed to settings
        """
        let = kwargs.pop('let', {})
        if '.' in cmd:
            command = fabfile
            for compo in cmd.split('.'):
                command = getattr(command, compo, command)
        else:
            command = getattr(fabfile.tasks, cmd, None)
        if not isinstance(command, tasks.WrappedCallableTask):
            raise RuntimeError("Unknown Fabric command %s" % cmd)
        with context_managers.settings(context_managers.hide('stdout'), **let):
            api.execute(command, *args, **kwargs)
        return self


class BuildDockerSimple(DockerImageMixin, FabricDeployMixin):

    def __init__(self, distrib='debian8', platform='simple', image=None, container=None, host=None, **options):
        self.host = host or platform
        self.distrib = distrib
        self.platform = platform
        self.set_path(os.path.join(DOCKER_ROOT, distrib))
        if not image:
            image = IMAGE_PREFIX + distrib
        self.image_name = image
        if not container:
            container = CONTAINER_PREFIX + platform
            self.short_container_name = platform
        else:
            self.short_container_name = container
        self.container_name = container
        self.container = None
        self.process_options(**options)

    def __str__(self):
        return 'BuildDockerSimple image:%s container:%s' % (self.image_name, self.container)
    __repr__ = __str__


class DockerImage(DockerImageMixin):

    def __init__(self, name, distrib, platform, **options):
        self.host = name
        self.container_name = CONTAINER_PREFIX + platform + '_' + name
        self.short_container_name = platform
        self.image_name = IMAGE_PREFIX + distrib + '_' + name
        self.set_path(os.path.join(DOCKER_ROOT, distrib, name))
        self.container = None
        self.process_options(**options)


class BuildDockerCompose(FabricDeployMixin):

    def __init__(self, distrib='debian8', platform='composed', template=None):
        self.distrib = distrib
        self.platform = platform
        self.images = {}
        self.template_images = []
        self.template = Environment(loader=FileSystemLoader(os.path.join(ROOT, 'templates')),
           trim_blocks=True, lstrip_blocks=True).get_template((template or platform) + '.yml.jinja')

    def __str__(self):
        return 'BuildDockerCompose images:%s containers:%s' % (self.images.keys(),
                                                               [i.container[:8] for i in self.images.itervalues()])
    __repr__ = __str__

    def add_image(self, name, **options):
        img = DockerImage(name, self.distrib, self.platform, **options)
        self.images[name] = img
        expose = options.get('expose')
        if expose:
            _expose = []
            for exp in expose:
                if isinstance(exp, basestring) and '-' in exp:
                    start, end = exp.split('-')
                    _expose.extend(range(int(start), int(end) + 1))
                else:
                    _expose.append(int(exp))
            expose = sorted(_expose)
        self.template_images.append({'name': name, 'image': img.image_name,
                                     'links': options.get('links'), 'ports': img.ports,
                                     'expose': expose, 'volumes': options.get('volumes')})
        return self

    def set_container(self):
        for img in self.images.itervalues():
            img.container = find_container(image=img.image_name)['Id']
        return self

    def reset_container(self):
        for img in self.images.itervalues():
            img.container = None
        return self

    def get_host(self):
        self.set_container()
        return dict((k, v.get_host()) for k, v in self.images.iteritems())

    def build(self):
        for img in self.images.itervalues():
            img.build()
        return self

    def destroy(self):
        for img in self.images.itervalues():
            try:
                img.destroy()
            except docker.errors.APIError:
                print("No immage " + img.image_name)
        return self

    def commit(self):
        for img in self.images.itervalues():
            img.commit()
        return self

    def create_yaml(self):
        with open(os.path.join(ROOT, 'docker-compose.yml'), 'w') as f:
            f.write(self.template.render(images=self.template_images))
        return self

    def compose_cmd(self, cmd):
        oldir = os.getcwd()
        os.chdir(ROOT)
        try:
            api.local('docker-compose ' + cmd)
        finally:
            os.chdir(oldir)
        return self

    def up(self):
        return self.create_yaml().compose_cmd('up -d').set_container()

    def start(self, compose=True):
        """
        start a platform globaly via compose
        or incrementaly via docker
        """
        if compose:
            return self.compose_cmd('start')
        else:
            for img in self.images.itervalues():
                img.start()
        return self

    def stop(self):
        return self.compose_cmd('stop')

    def rm(self):
        return self.compose_cmd('rm -f').reset_container()

    def run(self, cmd, host=None, hosts=None, sudo=False):
        """
        run a shell command on a set of containers,
        updating an attribute as a dict of outputs
        """
        if host:
            hosts = [host]
        self.output = {}
        for h in hosts or self.images:
            img = self.images[h]
            img.run(cmd, sudo=sudo)
            self.output[h] = img.output
        return self
