FROM python

ARG CDFLOW_COMMIT_SHA=master

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
     apt-transport-https \
     ca-certificates \
     curl \
     software-properties-common \
     git \
     bash && \
    curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add - && \
    add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable" && \
    apt-get update && apt-get -y install docker-ce && \
    apt-get clean

RUN git clone https://github.com/mergermarket/cdflow /tmp/cdflow && \
    cd /tmp/cdflow && \
    git checkout "${CDFLOW_COMMIT_SHA}" && \
    cp cdflow.py /usr/local/bin/cdflow && \
    chmod +x /usr/local/bin/cdflow && \
    pip install pipenv && \
    pipenv install --deploy --system && \
    cd && \
    rm -rf /tmp/cdflow
