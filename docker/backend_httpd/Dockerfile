# Crafted with the help of the SCLOrg docs:
# https://github.com/sclorg/nginx-container/tree/master/1.20#3-prepare-an-application-inside-a-container

FROM openeuler/nginx:1.21.5-22.03-lts

LABEL maintainer="infra@openeuler.org"

COPY files/ /

RUN sed -i 's#/run/nginx.pid#/tmp/nginx.pid#' /etc/nginx/nginx.conf

USER nginx
