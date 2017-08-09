FROM ubuntu:zesty
FROM buildpack-deps:zesty
ENV LANG C.UTF-8
RUN apt-get update
RUN apt-get install -y python3.6 python3.6-dev git ca-certificates
RUN wget https://bootstrap.pypa.io/get-pip.py && \
    python3.6 get-pip.py && \
    rm get-pip.py
