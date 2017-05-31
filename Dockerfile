FROM centos:7

RUN yum install -y epel-release 
RUN yum install -y git python-pip
RUN pip install -U pip

RUN pip install pytest hypothesis mock

COPY requirements.txt .
RUN pip install -r requirements.txt

ENV PYTHONPATH /cdflow/
WORKDIR /cdflow/

COPY . .
