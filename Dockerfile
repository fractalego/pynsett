ARG PYTHON_VERSION="3.6"
FROM python:${PYTHON_VERSION} AS builder

RUN apt-get update
RUN apt-get install -qq -y curl
RUN apt-get install -qq -y build-essential python-dev
RUN pip3 install pynsett

ADD pynsett/ /usr/local/

ENV PORT="4001"
EXPOSE ${PORT}

CMD ["cd usr/local/ && python3 -m pynsett.server.server"]