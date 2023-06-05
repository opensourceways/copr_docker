FROM openeuler/openeuler:22.03
LABEL maintainer="infra@openeuler.org"

# Deployment instructions are described here
# https://github.com/praiskup/resalloc/blob/master/docs/start-resalloc-server.txt
#
# Copr production deployment is described here
# https://pagure.io/fedora-infra/ansible/blob/master/f/roles/copr/backend/tasks/resalloc.yml

# download EUR repo
RUN curl -o /etc/yum.repos.d/eur.repo -L https://eur.openeuler.openatom.cn/coprs/mywaaagh_admin/eur/repo/openeuler-22.03_LTS_SP1/mywaaagh_admin-eur-openeuler-22.03_LTS_SP1.repo

RUN dnf install -y ansible \
                   vim \
                   resalloc-4.9 \
                   resalloc-server-4.9 \
                   findutils \
                   openssh-clients \
                   python3-psycopg2 \
                   gcc \
                   perl \
                   openssl-devel \
                   make \
                   coreutils \
    && dnf clean all && rm -rf /var/cache/dnf

# 22.03's rustc is 1.60 which lower than resalloc-kubernetes required(1.64)
# so we try to get the nightly from rustup
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs |sh -s -- -y --default-toolchain nightly -c rust-std -c rust-src
# install the resalloc-kubernetes
RUN source $HOME/.cargo/env && cargo install resalloc-kubernetes --root . && install -m 755 bin/resalloc-kubernetes /
# copy filesystem setup
COPY files/ /
# cleanup
RUN dnf remove gcc perl make -y && dnf clean all && rm -rf /var/cache/dnf && chmod +x /home/resalloc/provision/local-*

RUN cd $(rpm -ql resalloc-server |grep alembic.ini |xargs dirname) \
    && alembic upgrade head
