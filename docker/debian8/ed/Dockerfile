FROM debian:8

RUN echo "export CONTAINER=DOCKER" >> /etc/profile
RUN echo "export PS1='\u@DB:\w$ '" >> /etc/profile
# hack to add loaclhost alias in /etc/hosts at startup
# may be obsolete with docker-compose 1.3 [http://stackoverflow.com/questions/29076194/using-add-host-or-extra-hosts-with-docker-compose]
RUN echo "grep -q -F '127.0.0.1    ed' /etc/hosts || echo '127.0.0.1    ed' | sudo tee -a /etc/hosts >/dev/null" >> /etc/profile

# systemd is removed and sysvinit is installed instead.
# As of may 2015, systemd is difficult to launch in a docker container, see http://developerblog.redhat.com/2014/05/05/running-systemd-within-docker-container/
# and if systemd is installed, some packages try to launch via systemctl (eg PostgreSQL) and fail
RUN apt-get update && apt-get install -y sysvinit-core python openssh-server sudo locales supervisor
RUN apt-get remove -y systemd
RUN apt-get install -y postgresql postgis postgresql-server-dev-all

RUN useradd -m -s /bin/bash git && echo "git:git" | chpasswd
RUN adduser git sudo
RUN echo "git ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# postgres allows connections from remote hosts
RUN echo 'host  all all 0.0.0.0/0 md5' >> /etc/postgresql/9.4/main/pg_hba.conf
RUN sed -i "/^#listen_addresses /c\listen_addresses = '*'" /etc/postgresql/9.4/main/postgresql.conf

RUN mkdir /var/run/sshd
RUN sed -i "s/#PasswordAuthentication yes/PasswordAuthentication no/" /etc/ssh/sshd_config
# SSH login fix. Otherwise user is kicked off after login
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

RUN mkdir -p /home/git/.ssh
COPY unsecure_key.pub /home/git/.ssh/authorized_keys
RUN chmod 644 /home/git/.ssh/authorized_keys

RUN sed -i "/^# fr_FR.UTF-8 UTF-8/c\fr_FR.UTF-8 UTF-8" /etc/locale.gen
RUN locale-gen fr_FR.UTF-8

EXPOSE 22 5432

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

CMD ["/usr/bin/supervisord"]
