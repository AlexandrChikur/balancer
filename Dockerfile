FROM python:3.10

WORKDIR /opt/load_balancer

ARG DEFAULT_CONF_PATH=/etc/load_balancer/
ARG DEFAULT_CONF_FILENAME=settings.yaml

ENV \
  # python
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONOPTIMIZE=1 \
  # poetry
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_VERSION=1.2.2 \
  # balancer
  DEFAULT_CONF_PATH=${DEFAULT_CONF_PATH} \
  DEFAULT_CONF_FILENAME=${DEFAULT_CONF_FILENAME}

RUN apt-get update \
    && apt-get install netcat -y \
    && python -m pip install --upgrade pip \
    && pip install "poetry==$POETRY_VERSION"

COPY ./$DEFAULT_CONF_FILENAME $DEFAULT_CONF_PATH
COPY poetry.lock ./pyproject.toml ./balancer.py  ./

RUN poetry install --only main

COPY ./balancer ./balancer

CMD python balancer.py --port 3333 --config $DEFAULT_CONF_PATH/$DEFAULT_CONF_FILENAME

