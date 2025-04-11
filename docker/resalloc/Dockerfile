FROM openeuler/openeuler:24.03-lts-sp1 AS base

RUN dnf -y update && dnf -y in openssl-devel curl gcc make perl autoconf

# try to get the nightly from rustup
ENV RUSTUP_DIST_SERVER=https://mirrors.ustc.edu.cn/rust-static
ENV RUSTUP_UPDATE_ROOT=https://mirrors.ustc.edu.cn/rust-static/rustup
RUN mkdir -p $HOME/.cargo/
ADD /cargo_config $HOME/.cargo/config

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs |sh -s -- -y --default-toolchain nightly -c rust-std -c rust-src

# install the resalloc-kubernetes
RUN source $HOME/.cargo/env && cargo install resalloc-kubernetes --root . && install -m 755 bin/resalloc-kubernetes /

FROM openeuler/openeuler:24.03-lts-sp1
LABEL maintainer="infra@openeuler.org"

COPY --from=base /resalloc-kubernetes /resalloc-kubernetes
# download EUR repo
RUN curl -o /etc/yum.repos.d/eur.repo -L https://eur.openeuler.openatom.cn/coprs/mywaaagh_admin/eur/repo/openeuler-24.03_LTS_SP1/mywaaagh_admin-eur-openeuler-24.03_LTS_SP1.repo

RUN dnf install -y ansible \
                   vim \
                   resalloc-4.9 \
                   resalloc-server-4.9 \
                   findutils \
                   openssh-clients \
                   python3-psycopg2 \
                   coreutils \
                   python3-requests \
                   python3-pyyaml \
    && dnf clean all && rm -rf /var/cache/dnf


# copy filesystem setup
COPY files/ /
# cleanup
RUN dnf clean all && rm -rf /var/cache/dnf && chmod +x /home/resalloc/provision/local-*

RUN cd $(rpm -ql resalloc-server |grep alembic.ini |xargs dirname) \
    && alembic upgrade head
