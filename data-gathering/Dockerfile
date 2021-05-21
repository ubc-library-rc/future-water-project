FROM python:3.9

VOLUME /var/log/docker


# Install developer dependencies
RUN apt-get update
RUN apt-get install --reinstall build-essential -y
RUN apt-get install -y gcc g++ libxml2-dev libxslt1-dev \
    libxslt-dev python-dev libffi-dev openssl libssl-dev \
    make git sudo
RUN apt-get install python3-dev -y
RUN apt-get install -y python3-lxml

# Install general dependencies
RUN apt-get install -y bash
RUN apt-get install -y curl
RUN apt-get install -y tor



COPY . /tmp/src

WORKDIR /tmp/src/

# Install python packages
RUN pip install --no-cache-dir --upgrade pip
RUN pip install -r requirements.txt

# Setup TOR
RUN ./setup_tor.sh
EXPOSE 9001 9030 9051

# RUN tail -f /var/log/tor/notices.log

HEALTHCHECK --timeout=5s CMD echo quit | curl -sS telnet://localhost:9051

RUN chmod a+x docker.sh

# Run container
CMD ["./docker.sh"]