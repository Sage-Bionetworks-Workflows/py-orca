FROM python:3.11.1

WORKDIR /usr/src/app

COPY dist/ dist/

ARG TARBALL_PATH

RUN python -m pip install ${TARBALL_PATH}[all]
