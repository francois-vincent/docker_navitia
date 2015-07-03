FROM debian:8
MAINTAINER François Vincent <francois.vincent@canaltp.fr>

ENV CONTAINER DOCKER
RUN echo "export CONTAINER=DOCKER" >> /etc/profile

RUN useradd git && echo "git:git" | chpasswd && adduser git sudo
RUN mkdir -p /home/git && chown -R git:git /home/git
RUN sed -i 's/home\/git:\/bin\/sh/home\/git:\/bin\/bash/g' /etc/passwd

# systemd is removed and sysvinit is installed instead.
# As of may 2015, systemd is difficult to launch in a docker container, see http://developerblog.redhat.com/2014/05/05/running-systemd-within-docker-container/
# and if systemd is installed, some packages try to launch via systemctl (eg PostgreSQL) and fail
RUN apt-get update && apt-get install -y sysvinit-core python openssh-server sudo locales
RUN apt-get remove -y systemd
RUN apt-get install -y apache2 libapache2-mod-wsgi postgis postgresql-server-dev-all rabbitmq-server redis-server
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN adduser git www-data
RUN echo "git ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

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

EXPOSE 22 80 85 5432 5672

RUN mkdir /etc/apache2/conf.d
RUN echo "Include conf.d/" >> /etc/apache2/apache2.conf
RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf

# share file with other machine
VOLUME ["/srv/ed/data"]
RUN chmod a+w /srv/ed/data
RUN echo "export BINDED_VOLUMES=/srv/ed/data" >> /etc/profile

CMD ["/usr/sbin/sshd", "-D"]
