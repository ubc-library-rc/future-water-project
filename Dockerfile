FROM python:3

COPY ./data-visualization /tmp/src

COPY ./data-gathering/resources/keywords_final.json /tmp/src/scholia/resources/keywords_final.json

WORKDIR /tmp/src/

# Install developer dependencies
RUN apt-get update

# Install general dependencies
RUN apt-get install -y bash
RUN apt-get install -y curl

# Install python packages
RUN pip install --no-cache-dir --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8100

CMD ["python", "./runserver.py"]