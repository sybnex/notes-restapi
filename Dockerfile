FROM alpine:3.14
LABEL maintainer="sybnex"

ENV PYTHONPATH=/app

COPY requirements.txt /
RUN apk --no-cache add py3-pip py3-cryptography \
    && pip3 install --upgrade pip \
    && pip3 install -r /requirements.txt --no-cache-dir \
    && adduser -D note

COPY app /app
RUN chown -R note /app/ \
    && flake8 /app/run.py \
    && python3 -m compileall /app/*.py

USER note
WORKDIR /app
CMD [ "python3", "/app/run.py" ]
