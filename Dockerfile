# Dockerfile


FROM debian:jessie

RUN true \
 && apt-get -q update \
 && DEBIAN_FRONTEND=noninteractive apt-get -qy --no-install-recommends install python3 python3-pip \
 && rm -rf /var/lib/apt/lists/* \
 && true

RUN true \
 && apt-get -q update \
 && DEBIAN_FRONTEND=noninteractive apt-get -qy --no-install-recommends install git python3-lxml python3-yaml \
 && rm -rf /var/lib/apt/lists/* \
 && true

EXPOSE 6543

WORKDIR /opt/service
CMD ["./run.sh"]
COPY run.sh run.sh

COPY config.ini config.ini

COPY requirements.txt /tmp/requirements.txt
RUN true \
 && DEBIAN_FRONTEND=noninteractive pip3 install -q -r /tmp/requirements.txt \
 && true

COPY . /tmp/build
RUN true \
 && DEBIAN_FRONTEND=noninteractive pip3 install -q /tmp/build \
 && rm -rf /tmp/build \
 && true


# EOF
