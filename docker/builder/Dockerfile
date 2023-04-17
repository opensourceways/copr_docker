FROM registry.fedoraproject.org/fedora:37
LABEL maintainer="infra@openeuler.org"

ARG ADDITIONAL_COPR_REPOSITORIES="@copr/copr"

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
                   python3-pip \
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
                   patch \
    && dnf -y install copr-rpmbuild-0.64 nosync-1.1 copr-builder-0.64 copr-distgit-client-0.64 \
    && dnf -y downgrade nosync && dnf clean all && rm -rf /var/cache/dnf

COPY files/ /

# needed to run sshd
RUN ssh-keygen -f /etc/ssh/ssh_host_rsa_key -N '' -q
# setup mock user
RUN useradd -m -u 1000 -g 135 -n mockbuild && \
    mkdir -p /home/mockbuild/.ssh && chmod 700 /home/mockbuild /home/mockbuild/.ssh && \
    touch /home/mockbuild/.ssh/authorized_keys && chmod 600 /home/mockbuild/.ssh/authorized_keys && \
    cat /home/mockbuild/.ssh/id_backend.pub >> /home/mockbuild/.ssh/authorized_keys && \
    cp -r /home/mockbuild/.ssh /root/ && \
    chown mockbuild:135 /home/mockbuild -R

# using huawei cloud mirrors
RUN sed -i 's/metalink=/#metalink=/g' /etc/yum.repos.d/* \
    && sed -i 's/#baseurl=/baseurl=/g' /etc/yum.repos.d/* \
    && sed -i 's/download.example\/pub\/fedora\/linux/mirrors.huaweicloud.com\/fedora/g' /etc/yum.repos.d/*

RUN echo 'config_opts["use_nspawn"] = False' >> /etc/mock/site-defaults.cfg

# do some patch works
RUN patch /usr/lib/python3.11/site-packages/copr_rpmbuild/providers/pypi.py < /pypi.patch && \
    patch /usr/lib/python3.11/site-packages/copr_rpmbuild/providers/rubygems.py < /rubygems.patch && \
    patch /usr/lib/python3.11/site-packages/copr_rpmbuild/providers/scm.py < /scm.patch
# install pyporter & rubyporter
# using ADD to skip cache
ADD "https://gitee.com/api/v5/repos/mywaaagh_admin/pyporter/commits?page=1&per_page=1" pyporter_last_commit
RUN git clone https://gitee.com/mywaaagh_admin/pyporter && cd pyporter && python3 -m pip install .

ADD "https://gitee.com/api/v5/repos/openeuler/rubyporter/commits?page=1&per_page=1" rubyporter_last_commit
RUN git clone https://gitee.com/openeuler/rubyporter && cd rubyporter && python3 -m pip install .

CMD ["/usr/sbin/sshd", "-D"]
