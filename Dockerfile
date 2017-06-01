FROM centos:7

RUN yum install -y epel-release 
RUN yum install -y git python-pip
RUN pip install -U pip

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN pip install pytest pytest-cov pytest-randomly hypothesis mock flake8 mccabe

ENV PYTHONPATH /cdflow/
WORKDIR /cdflow/

COPY . .
