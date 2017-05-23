FROM centos:7

RUN yum install -y git curl
RUN cd /tmp/ && \
    curl -OL https://github.com/sstephenson/bats/archive/master.tar.gz && \
    tar xzf master.tar.gz && \
    cd bats-master && \
    ./install.sh /usr/local/

COPY . /bats
WORKDIR /bats

ENTRYPOINT ["bats"]
