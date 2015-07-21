FROM debian:8

RUN echo "export CONTAINER=DOCKER" >> /etc/profile

# systemd is removed and sysvinit is installed instead.
# As of may 2015, systemd is difficult to launch in a docker container, see http://developerblog.redhat.com/2014/05/05/running-systemd-within-docker-container/
# and if systemd is installed, some packages try to launch via systemctl (eg PostgreSQL) and fail
RUN apt-get update && apt-get install -y sysvinit-core python openssh-server sudo locales supervisor
RUN apt-get remove -y systemd
RUN apt-get install -y apache2 libapache2-mod-wsgi
RUN apt-get install -y  postgresql-server-dev-all postgis
RUN apt-get install -y redis-server rabbitmq-server

# change redis-server conf for not daemonize (for supervisord)
RUN sed -i '/^daemonize yes/c\daemonize no' /etc/redis/redis.conf

# add user navitia, as a sudoer (for later tests and debug)
RUN useradd -m -s /bin/bash navitia && echo "navitia:navitia" | chpasswd
RUN adduser navitia sudo && adduser navitia www-data
RUN echo "navitia ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
RUN echo "export PS1='\u@NAVITIA:\w$ '" >> /home/navitia/.bashrc

# configure SSH server
RUN mkdir /var/run/sshd
RUN mkdir -p /home/navitia/.ssh
# SSH login fix. Otherwise user is kicked off after login
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd
COPY unsecure_key.pub /home/navitia/.ssh/authorized_keys
RUN chmod 644 /home/navitia/.ssh/authorized_keys

# set locale to French
RUN sed -i "/^# fr_FR.UTF-8 UTF-8/c\fr_FR.UTF-8 UTF-8" /etc/locale.gen
RUN locale-gen fr_FR.UTF-8

# set basic Apache config
RUN mkdir /etc/apache2/conf.d
RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf
RUN echo "Include conf.d/" >> /etc/apache2/apache2.conf

# ports
EXPOSE 22 80 85

# volumes
ENV DATA_VOLUME /srv/ed/data
VOLUME ["$DATA_VOLUME"]
RUN chmod a+rw $DATA_VOLUME

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

CMD ["/usr/bin/supervisord"]
