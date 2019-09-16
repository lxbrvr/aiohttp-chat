FROM python:3.7-alpine3.8

RUN apk --no-cache --update-cache add gcc python3-dev build-base git && \
    pip install --upgrade pip setuptools && \
    mkdir -p /app

ENV PYTHONUNBUFFERED=true

COPY ./requirements.txt /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt

COPY src /app/src

WORKDIR /app

CMD ["python", "src/cli.py", "run", "--port", "8000"]