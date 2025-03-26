FROM openeuler/openeuler:24.03 AS base

RUN dnf -y update && dnf -y in git gcc openssl-devel protobuf-c-devel make
# prepare rust toolchain
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs |sh -s -- -y --default-toolchain nightly -c rust-std -c rust-src
RUN git clone https://gitee.com/openeuler/signatrust.git && source $HOME/.cargo/env && cd signatrust && cargo build --bin client --release && install -m 755 target/release/client /usr/local/bin/

FROM openeuler/openeuler:24.03 AS backend
LABEL maintainer="infra@openeuler.org"

ENV export LANG=en_US.UTF-8
ENV PYTHONPATH="/usr/share/copr/"

COPY --from=base /usr/local/bin/client /usr/local/bin/client

# TERM is to make the tito work in container, rhbz#1733043
ENV TERM=linux \
    LANG=en_US.UTF-8

# download EUR repo
RUN curl -o /etc/yum.repos.d/eur.repo -L https://eur.openeuler.openatom.cn/coprs/mywaaagh_admin/eur/repo/openeuler-24.03_LTS_SP1/mywaaagh_admin-eur-openeuler-24.03_LTS_SP1.repo

RUN set -ex ; \
    dnf -y install dnf-plugins-core && dnf -y update && \
    dnf -y install htop \
                   make \
                   wget \
                   net-tools \
                   iputils \
                   vim \
                   mlocate \
                   git \
                   sudo \
                   openssh-server \
                   resalloc \
                   psmisc \
                   nginx \
                   python3-ipdb \
                   findutils \
                   tini \
                   patch \
# to get more entropy for generation of gpg keys
                   rng-tools \
                   openstack-release-antelope \
# for unbuffer package
                   expect \
                   python3-kafka-python \
    && dnf -y install copr-backend-1.177 \
    && dnf clean all && rm -rf /var/cache/dnf




# needed to be able to ping
RUN setcap cap_net_raw,cap_net_admin+p /usr/bin/ping

# needed to run sshd
RUN ssh-keygen -f /etc/ssh/ssh_host_rsa_key -N '' -q

# setup root user
RUN mkdir -p /root/.ssh && chmod 700 /root /root/.ssh

# setup copr user
RUN set -x ; \
    echo 'copr ALL=(ALL:ALL) NOPASSWD:ALL' >> /etc/sudoers && \
    mkdir -p /home/copr/.ssh && chmod 700 /home/copr /home/copr/.ssh && \
    mkdir -p /home/copr/.gnupg && chown copr:copr -R /home/copr

# system setup for copr-backend
RUN usermod -a -G mock copr && usermod -u 989 copr && groupmod -g 988 copr

# copy filesystem setup and setup ownership and permissions
COPY files/ /
RUN chmod 700 /root && \
    chmod 700 /home/copr && \
    chown -R copr:copr /home/copr

# Copr user needs permissions for /bin/sign.  We drop the setuid bit here as in
# container scenario it is not desired.  We use the downstream-only option
# allow-unprivileged-ports option: https://github.com/openSUSE/obs-sign/pull/36
RUN chmod 0755 /usr/bin/sign
RUN chmod 0755 /run-backend

# entrypoint needs to have write access here (group=0)
RUN chown copr:root /etc/sign.conf && \
    chmod 0660 /etc/sign.conf


# Not sure why the directory wasn't created automatically
RUN mkdir /var/lock/copr-backend
RUN chown copr:copr /var/lock/copr-backend /var/log/copr-backend

USER copr
RUN ln -sf /proc/1/fd/1 /var/log/copr-backend/action_dispatcher.log && \
              ln -sf /proc/1/fd/1 /var/log/copr-backend/build_dispatcher.log && \
              ln -sf /proc/1/fd/1 /var/log/copr-backend/actions.log && \
              ln -sf /proc/1/fd/1 /var/log/copr-backend/analyze-results.log && \
              ln -sf /proc/1/fd/1 /var/log/copr-backend/backend.log && \
              ln -sf /proc/1/fd/1 /var/log/copr-backend/logger.log && \
              ln -sf /proc/1/fd/1 /var/log/copr-backend/modifyrepo.log && \
              ln -sf /proc/1/fd/1 /var/log/copr-backend/pruner.log && \
              ln -sf /proc/1/fd/1 /var/log/copr-backend/spawner.log && \
              ln -sf /proc/1/fd/1 /var/log/copr-backend/terminator.log && \
              ln -sf /proc/1/fd/1 /var/log/copr-backend/vmm.log && \
              ln -sf /proc/1/fd/1 /var/log/copr-backend/worker.log
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/run-backend"]
