FROM registry.fedoraproject.org/fedora:37
LABEL maintainer="infra@openeuler.org"

ARG ADDITIONAL_COPR_REPOSITORIES="@copr/copr-dev"

# TERM is to make the tito work in container, rhbz#1733043
ENV TERM=linux

# base packages
RUN set -ex ; \
    rm /etc/yum.repos.d/fedora-cisco-openh264.repo && \
    test -z "${ADDITIONAL_COPR_REPOSITORIES}" \
        || dnf -y install dnf-plugins-core \
        && for repo in $ADDITIONAL_COPR_REPOSITORIES ; do dnf -y copr enable $repo; done ; \
    dnf -y update && \
    dnf -y install htop \
                   which \
                   wget \
                   vim \
                   python3-ipdb \
                   openssh-server \
                   fedora-packager \
                   mock \
                   mock-lvm \
                   createrepo \
                   yum-utils \
                   rsync \
                   openssh-clients \
                   rpm \
                   glib2 \
                   ca-certificates \
                   scl-utils-build \
                   ethtool \
                   git \
    && dnf -y install copr-builder \
    && dnf clean all

COPY files/ /
RUN mv /pypi.py /usr/lib/python*/site-packages/copr_rpmbuild/providers/ && \
    mv /rubygems.py /usr/lib/python*/site-packages/copr_rpmbuild/providers/

RUN dnf -y downgrade nosync \
    && dnf -y downgrade nosync && dnf clean all
# needed to run sshd
RUN ssh-keygen -f /etc/ssh/ssh_host_rsa_key -N '' -q
# install pyporter & rubyporter
RUN git clone https://gitee.com/openeuler/pyporter.git && cd pyporter && python3 setup.py install
RUN git clone https://gitee.com/openeuler/rubyporter.git && cd rubyporter && python3 setup.py install
# setup root user
RUN echo 'root:passwd' | chpasswd && \
    chmod 700 /root /root/.ssh && \
    touch /root/.ssh/authorized_keys && chmod 600 /root/.ssh/authorized_keys && \
    cat /root/.ssh/id_backend.pub >> /root/.ssh/authorized_keys

# using huawei cloud mirrors
RUN sed -i 's/metalink=/#metalink=/g' /etc/yum.repos.d/* \
    && sed -i 's/#baseurl=/baseurl=/g' /etc/yum.repos.d/* \
    && sed -i 's/download.example\/pub\/fedora\/linux/mirrors.huaweicloud.com\/fedora/g' /etc/yum.repos.d/*

RUN echo 'config_opts["use_nspawn"] = False' >> /etc/mock/site-defaults.cfg

CMD ["/usr/sbin/sshd", "-D"]
