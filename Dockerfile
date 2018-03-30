From alpine:3.7

RUN apk update && \
    apk add python3 supervisor && \
    pip3 install --upgrade pip && \
    pip3 install flask gunicorn flask-cors && \
    rm -rf /var/cache/apk/*

RUN mkdir /app

COPY app/ /app/

EXPOSE 5000

CMD ["supervisord", "-c", "/app/conf/supervisord.conf"]

#CMD ["cat", "/app/conf/supervisord.conf"]
