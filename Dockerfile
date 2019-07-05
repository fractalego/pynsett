ARG PYTHON_VERSION="3.6"
FROM python:${PYTHON_VERSION} AS builder

RUN apt-get update
RUN apt-get install -qq -y curl
RUN apt-get install -qq -y build-essential python-dev
RUN apt-get install -qq -y wget

WORKDIR /usr/local/
COPY pynsett pynsett/

RUN wget https://allennlp.s3.amazonaws.com/models/coref-model-2018.02.05.tar.gz
RUN cp coref-model-2018.02.05.tar.gz pynsett/data/

COPY requirements.txt /
RUN pip install -r /requirements.txt
RUN python -m spacy download en_core_web_lg
RUN python -m spacy link en_core_web_lg en_core_web_sm
RUN python -m nltk.downloader punkt

ENV PORT="4001"
EXPOSE ${PORT}

CMD ["python", "-m", "pynsett.server.server"]