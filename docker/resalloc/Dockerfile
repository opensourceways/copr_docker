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
                   resalloc-4.9 \
                   resalloc-aws-1.3 \
                   resalloc-server-4.9 \
                   findutils \
                   openssh-clients \
                   python3-psycopg2 \
                   gcc \
                   cargo \
                   perl \
    && dnf clean all && rm -rf /var/cache/dnf

# install the resalloc-kubernetes
RUN cargo install resalloc-kubernetes --root . && mv bin/resalloc-kubernetes /
# copy filesystem setup
COPY files/ /
# cleanup
RUN dnf remove gcc cargo perl -y && dnf clean all && rm -rf /var/cache/dnf && chmod +x /home/resalloc/provision/local-*

RUN cd $(rpm -ql resalloc-server |grep alembic.ini |xargs dirname) \
    && alembic-3 upgrade head && chmod 755 /resalloc-kubernetes
