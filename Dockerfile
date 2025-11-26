FROM debian:bookworm

RUN apt update -y && \
    apt install -y ca-certificates apt-transport-https gnupg

COPY contrib/deb.oxen.io.gpg /etc/apt/trusted.gpg.d/oxen.gpg
RUN echo "deb [signed-by=/etc/apt/trusted.gpg.d/oxen.gpg] http://deb.oxen.io/ bookworm main" > /etc/apt/sources.list.d/oxen.list

RUN apt update -y && \
    apt install -y --no-install-recommends python3 \
        python3-pytest \
        python3-oxenmq \
        python3-oxenc \
        python3-pyonionreq \
        python3-coloredlogs \
        python3-uwsgidecorators \
        python3-flask \
        python3-cryptography \
        python3-pycryptodome \
        python3-nacl \
        python3-pil \
        python3-protobuf \
        python3-openssl \
        python3-qrcode \
        python3-better-profanity \
        python3-sqlalchemy \
        python3-sqlalchemy-utils \
        uwsgi-plugin-python3


COPY sogs /usr/lib/python3/dist-packages/sogs
COPY contrib/docker-entrypoint.py /usr/bin/docker-entrypoint.py
COPY contrib/uwsgi-docker.ini /etc/uwsgi-docker.ini
RUN chmod +x /usr/bin/docker-entrypoint.py

USER www-data
VOLUME /var/lib/sogs
WORKDIR /var/lib/sogs
EXPOSE 8080

#ENV SOGS_DB_URL=sqlite:///var/lib/sogs/sogs.db

ENV DB_PATH=/var/lib/sogs/sogs.db

ENV SOGS_NET_BASE_URL=http://localhost:8080
ENV SOGS_USERS_REQUIRE_BLIND_KEYS=true
ENV SOGS_CRYPTO_KEY_FILE=/var/lib/sogs/key_x25519


ENTRYPOINT ["python3", "/usr/bin/docker-entrypoint.py"]