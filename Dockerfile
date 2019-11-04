FROM alpine
LABEL maintainer="sybnex"

ENV PYTHONPATH=/app

RUN apk --no-cache add python3 py3-cryptography \
    && pip3 install --upgrade pip \
    && pip3 install flask flask-restful requests python-telegram-bot datetime --no-cache-dir \
    && adduser -D note

COPY app /app

RUN chown -R note /app/ \
    && python3 -m compileall /app/*.py

USER note
WORKDIR /app

CMD [ "python3", "/app/run.py" ] 
