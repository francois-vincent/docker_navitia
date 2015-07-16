FROM debian:8
MAINTAINER François Vincent <francois.vincent@canaltp.fr>

ENV CONTAINER DOCKER
RUN echo "export CONTAINER=DOCKER" >> /etc/profile
ENV DOCKER_IMAGE TYR
RUN echo "export DOCKER_IMAGE=TYR" >> /etc/profile
RUN echo "export PS1='\u@$DOCKER_IMAGE:\w$ '" >> /etc/profile
# hack to add loaclhost alias in /etc/hosts at startup
# may be obsolete with docker-compose 1.3 [http://stackoverflow.com/questions/29076194/using-add-host-or-extra-hosts-with-docker-compose]
RUN echo "grep -q -F '127.0.0.1    tyr' /etc/hosts || echo '127.0.0.1    tyr' | sudo tee -a /etc/hosts >/dev/null" >> /etc/profile

# systemd is removed and sysvinit is installed instead.
# As of may 2015, systemd is difficult to launch in a docker container, see http://developerblog.redhat.com/2014/05/05/running-systemd-within-docker-container/
# and if systemd is installed, some packages try to launch via systemctl (eg PostgreSQL) and fail
RUN apt-get update && apt-get install -y sysvinit-core python openssh-server sudo locales
RUN apt-get remove -y systemd
RUN apt-get install -y rabbitmq-server redis-server

RUN useradd -m -s /usr/bash git && echo "git:git" | chpasswd
RUN adduser git sudo && adduser git www-data
RUN echo "git ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# allow user 'guest' from remote hosts
RUN echo '[{rabbit, [{loopback_users, []}]}].' > /etc/rabbitmq/rabbitmq.config

RUN mkdir /var/run/sshd
RUN sed -i "s/#PasswordAuthentication yes/PasswordAuthentication no/" /etc/ssh/sshd_config
# SSH login fix. Otherwise user is kicked off after login
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile
RUN mkdir -p /home/git/.ssh
COPY unsecure_key.pub /home/git/.ssh/authorized_keys
RUN chmod 644 /home/git/.ssh/authorized_keys

RUN sed -i "/^# fr_FR.UTF-8 UTF-8/c\fr_FR.UTF-8 UTF-8" /etc/locale.gen
RUN locale-gen fr_FR.UTF-8

EXPOSE 22 5672

# share file with other machine
VOLUME ["/srv/ed/data"]
RUN echo "sudo chmod a+w /srv/ed/data" >> /etc/profile
RUN echo "export BINDED_VOLUMES='/srv/ed/data'" >> /etc/profile

CMD ["/usr/sbin/sshd", "-D"]
