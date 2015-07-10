FROM debian:8
MAINTAINER François Vincent <francois.vincent@canaltp.fr>

RUN echo "export CONTAINER=DOCKER" >> /etc/profile
RUN echo "export PS1='\u@NAVITIA:\w$ '" >> /etc/profile

# systemd is removed and sysvinit is installed instead.
# As of may 2015, systemd is difficult to launch in a docker container, see http://developerblog.redhat.com/2014/05/05/running-systemd-within-docker-container/
# and if systemd is installed, some packages try to launch via systemctl (eg PostgreSQL) and fail
RUN apt-get update && apt-get install -y sysvinit-core python openssh-server sudo locales supervisor
RUN apt-get remove -y systemd
RUN apt-get install -y apache2 libapache2-mod-wsgi
RUN apt-get install -y  postgresql-server-dev-all postgis
RUN apt-get install -y redis-server rabbitmq-server

# change redis-server conf for not daemonize
RUN sed -i '/^daemonize yes/c\daemonize no' /etc/redis/redis.conf

RUN useradd git && echo "git:git" | chpasswd && adduser git sudo
RUN mkdir -p /home/git && chown -R git:git /home/git
RUN sed -i 's/home\/git:\/bin\/sh/home\/git:\/bin\/bash/g' /etc/passwd
RUN adduser git www-data
RUN echo "git ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

RUN mkdir /var/run/sshd
RUN sed -i "s/#PasswordAuthentication yes/PasswordAuthentication no/" /etc/ssh/sshd_config
# SSH login fix. Otherwise user is kicked off after login
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

RUN mkdir -p /home/git/.ssh
COPY unsecure_key.pub /home/git/.ssh/authorized_keys
RUN chmod 644 /home/git/.ssh/authorized_keys

RUN sed -i "/^# fr_FR.UTF-8 UTF-8/c\fr_FR.UTF-8 UTF-8" /etc/locale.gen
RUN locale-gen fr_FR.UTF-8

EXPOSE 22 80 85

RUN mkdir /etc/apache2/conf.d
RUN echo "Include conf.d/" >> /etc/apache2/apache2.conf
RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf

# volumes
ENV DATA_VOLUME /srv/ed/data
VOLUME ["$DATA_VOLUME"]

# externalize data folder
RUN chmod a+rw $DATA_VOLUME
RUN echo "export DATA_VOLUME=$DATA_VOLUME" >> /etc/profile

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

CMD ["/usr/bin/supervisord"]
