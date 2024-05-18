FROM python:3.10

ENV PYTHONUNBUFFERED 1

COPY poetry.lock pyproject.toml /src/

WORKDIR /src/
RUN pip install poetry

RUN poetry install
COPY . /src/
EXPOSE 8000