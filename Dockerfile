FROM python:3.12-slim

WORKDIR /app

# install apt packages
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install -y \
         nginx libnginx-mod-http-lua libsqlite3-dev luarocks \
    && luarocks install lsqlite3 \
    && apt remove -y luarocks \
    && apt autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements-dev.txt /app

RUN python3 -m pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY --chmod=755 *.py *.sh /usr/local/bin/
COPY --chmod=644 nginx.conf /etc/nginx/nginx.conf
COPY VERSION /app/VERSION

RUN mkdir -p /docker-volume /tmpfs

ENTRYPOINT ["/app/entrypoint.sh"]


# to run test
# docker run -it --rm --entrypoint /bin/bash -v %cd%:/app safe-proxy-docker
# pip install -r requirements-dev.txt && PYTHONPATH=. pytest

# to generate encrypted key
# docker compose run --rm --entrypoint /usr/local/bin/encrypt_key.py api_proxy YOUR_API_KEY
