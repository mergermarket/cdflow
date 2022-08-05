FROM python:3.10.6 AS base

COPY Pipfile Pipfile.lock ./
RUN pip install pipenv && pipenv install --system --deploy --dev

ENV PYTHONPATH /cdflow/
WORKDIR /cdflow/

ENV AWS_ACCESS_KEY_ID=1
ENV AWS_SECRET_ACCESS_KEY=1

COPY . .
