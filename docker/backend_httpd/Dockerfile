# Crafted with the help of the SCLOrg docs:
# https://github.com/sclorg/nginx-container/tree/master/1.20#3-prepare-an-application-inside-a-container

FROM quay.io/centos7/nginx-120-centos7

LABEL maintainer="infra@openeuler.org"

COPY files/etc/nginx/conf.d/copr-be.conf /opt/app-root/etc/nginx.d/

CMD nginx -g "daemon off;"
