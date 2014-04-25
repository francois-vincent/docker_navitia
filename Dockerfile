FROM debian
CMD mkdir -p /kraken
WORKDIR /kraken
RUN /usr/bin/apt-get update
RUN /usr/bin/apt-get -y install g++ cmake liblog4cplus-dev libzmq-dev libosmpbf-dev libboost-all-dev libpqxx3-dev libgoogle-perftools-dev libprotobuf-dev python-pip libproj-dev protobuf-compiler git libgeos-c1
RUN git clone git@github.com:CanalTP/navitia.git
RUN git submodule update --init 
RUN pip install -r /kraken/source/jormungandr/requirements.txt
RUN pip install -r /kraken/source/tyr/requirements.txt
RUN pip install honcho
RUN git submodule update 
RUN mkdir -p debug ; cd debug ;cmake ../source  ; make -j4
WORKDIR /kraken/jormungandr
