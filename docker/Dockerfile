FROM debian:buster

RUN apt-get update \
    && apt-get install -y python3-dev python3-opencv python3-funcsigs python3-apscheduler\
       python3-tornado python3-pil strace avrdude python3-scipy python3-pykka python3-semver\
       python3-requests python3-serial

RUN mkdir /fabscan && mkdir /fabscan/src && mkdir /fabscan/dummy

WORKDIR /fabscan
