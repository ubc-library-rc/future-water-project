FROM libraryrc/future-waters-base:latest
MAINTAINER marques.s.arthur@gmail.com

COPY . /tmp/src

WORKDIR /tmp/src/

# Setup TOR
RUN ./setup_tor.sh

EXPOSE 9001 9030 9051
CMD ["tor", "-f", "/data/torrc"]

HEALTHCHECK --timeout=5s CMD echo quit | curl -sS telnet://localhost:9051

RUN pwd

RUN ls -l resources

# Run container
ENTRYPOINT [ "python3" ]
CMD [ "test/test_pipeline_google.py" ]