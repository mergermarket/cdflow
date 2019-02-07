FROM python:3.7.2 AS base

COPY Pipfile Pipfile.lock ./
RUN pip install pipenv && pipenv install --system --deploy --dev

ENV PYTHONPATH /cdflow/
WORKDIR /cdflow/

COPY . .

FROM base AS build

RUN pip install pip==18.1 && \
    pip install pyinstaller staticx && \
    apt-get update && apt-get install -y patchelf

RUN pyinstaller \
    --hidden-import configparser \
    --onefile \
    --name "cdflow-$(uname -s)-$(uname -m)" \
    cdflow.py && \
    pyinstaller "cdflow-$(uname -s)-$(uname -m).spec" && \
    staticx "./dist/cdflow-$(uname -s)-$(uname -m)" \
        "cdflow-$(uname -s)-$(uname -m)" 
