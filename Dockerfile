FROM python:3.7.1 AS base

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY test_requirements.txt .
RUN pip install -r test_requirements.txt

ENV PYTHONPATH /cdflow/
WORKDIR /cdflow/

COPY . .

FROM base AS build

RUN pip install pyinstaller

RUN pyinstaller \
    --hidden-import configparser \
    --onefile \
    --name "cdflow-$(uname -s)-$(uname -m)" \
    cdflow.py && \
    pyinstaller cdflow.spec
