FROM debian
CMD mkdir -p /kraken
WORKDIR /kraken
RUN /usr/bin/apt-get update
RUN /usr/bin/apt-get -y install g++ cmake liblog4cplus-dev libzmq-dev libosmpbf-dev libboost-all-dev libpqxx3-dev libgoogle-perftools-dev libprotobuf-dev python-pip libproj-dev protobuf-compiler git
RUN mkdir -p /root/.ssh/
ADD ./id_rsa /root/.ssh/id_rsa
ADD ./config_ssh /root/.ssh/config
RUN git clone git@github.com:CanalTP/kraken.git /kraken/ -o StrictHostKeyChecking=no
RUN git submodule update --init 
RUN pip install -r /kraken/source/jormungandr/requirements.txt
RUN pip install -r /kraken/source/tyr/requirements.txt
CMD git fetch origin
CMD git checkout dev
CMD git rebase origin/dev
CMD git submodule update 
CMD mkdir -p debug ; cd debug ;cmake ../source  ; make -j4
