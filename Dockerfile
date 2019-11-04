FROM alpine
LABEL maintainer="sybnex"

ENV PYTHONPATH=/app

RUN apk --no-cache add python3 \
    && pip3 install --upgrade pip \
    && pip3 install flask flask-restful gunicorn --no-cache-dir \
    && adduser -D note

COPY app /app

RUN chown -R note /app/ \
    && python3 -m compileall /app/*.py

USER note
WORKDIR /app

CMD [ "gunicorn", "-w4", "-b0.0.0.0:5000", "--log-level=INFO", "run:app" ] 
