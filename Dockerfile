ARG PYTHON_VERSION="3.6"
FROM python:${PYTHON_VERSION} AS builder

RUN apt-get update
RUN apt-get install -qq -y curl
RUN apt-get install -qq -y build-essential python-dev

WORKDIR /usr/local/
COPY pynsett pynsett/

COPY requirements.txt /
RUN pip install -r /requirements.txt
RUN python -m spacy download en_core_web_sm
RUN python -m spacy download en_core_web_lg
RUN python -m nltk.downloader punkt

ENV PORT="4001"
EXPOSE ${PORT}

CMD ["python", "-m", "pynsett.server.server"]