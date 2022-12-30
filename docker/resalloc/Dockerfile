FROM registry.fedoraproject.org/fedora:37
LABEL maintainer="infra@openeuler.org"
ARG TARGETARCH
# Deployment instructions are described here
# https://github.com/praiskup/resalloc/blob/master/docs/start-resalloc-server.txt
#
# Copr production deployment is described here
# https://pagure.io/fedora-infra/ansible/blob/master/f/roles/copr/backend/tasks/resalloc.yml

RUN dnf install -y ansible \
                   vim \
                   resalloc \
                   resalloc-aws \
                   resalloc-server \
                   sqlite \
                   findutils \
                   openssh-clients \
    && dnf clean all

# copy filesystem setup
COPY files/ /
RUN mv /resalloc-kubernetes-$TARGETARCH /resalloc-kubernetes

RUN cd $(rpm -ql resalloc-server |grep alembic.ini |xargs dirname) \
    && alembic-3 upgrade head && chmod 755 /resalloc-kubernetes
