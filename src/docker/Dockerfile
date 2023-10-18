FROM python:3.11.6

WORKDIR /usr/src/app

COPY dist/ dist/

ARG TARBALL_PATH

RUN python -m pip install ${TARBALL_PATH}[all]
