FROM python:3.7.1 AS base

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN pip install pytest pytest-cov pytest-randomly hypothesis mock flake8 mccabe

ENV PYTHONPATH /cdflow/
WORKDIR /cdflow/

COPY . .

FROM base AS build

RUN pip install pyinstaller

RUN pyinstaller --onefile cdflow.py && \
    pyinstaller cdflow.spec
