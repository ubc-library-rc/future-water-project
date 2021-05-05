FROM libraryrc/future-waters-base:latest

COPY . /tmp/src

WORKDIR /tmp/src/

# Setup TOR
RUN ./setup_tor.sh
EXPOSE 9001 9030 9051

# RUN tail -f /var/log/tor/notices.log

HEALTHCHECK --timeout=5s CMD echo quit | curl -sS telnet://localhost:9051

RUN chmod a+x docker.sh

# Run container
CMD ["./docker.sh"]