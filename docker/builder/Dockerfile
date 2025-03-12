FROM openeuler/openeuler:24.03-lts
LABEL maintainer="infra@openeuler.org"

# TERM is to make the tito work in container, rhbz#1733043
ENV TERM=linux

COPY files/ /

# download EUR repo
RUN curl -o /etc/yum.repos.d/eur.repo -L https://eur.openeuler.openatom.cn/coprs/mywaaagh_admin/eur/repo/openeuler-24.03_LTS_SP1/mywaaagh_admin-eur-openeuler-24.03_LTS_SP1.repo
# install old nosync for ABI compatible
RUN dnf -y update && dnf -y in nosync && rm -f /etc/yum.repos.d/eur.repo

# download EUR repo
RUN curl -o /etc/yum.repos.d/eur1.repo -L https://eur.openeuler.openatom.cn/coprs/mywaaagh_admin/eur/repo/openeuler-24.03_LTS_SP1/mywaaagh_admin-eur-openeuler-24.03_LTS_SP1.repo
RUN curl -o /etc/yum.repos.d/eur2.repo -L https://eur.openeuler.openatom.cn/coprs/fuyong666/eur/repo/openeuler-24.03_LTS_SP1/fuyong666-eur-openeuler-24.03_LTS_SP1.repo

# base packages
RUN set -ex ; \
    dnf -y update && \
    dnf -y install htop \
                   which \
                   wget \
                   vim \
                   python3-ipdb \
                   python3-pip \
                   openssh-server \
                   mock \
                   mock-lvm \
                   createrepo \
                   rsync \
                   openssh-clients \
                   rpm \
                   glib2 \
                   ca-certificates \
                   scl-utils-build \
                   ethtool \
                   git \
                   patch \
                   python3-pyyaml \
                   python3-wheel \
                   make \
                   gem \
    && dnf -y install git-lfs \
    && dnf -y install copr-rpmbuild-0.68 copr-builder-0.68 copr-distgit-client-0.68 \
    && dnf clean all && rm -rf /var/cache/dnf

# needed to run sshd
RUN ssh-keygen -f /etc/ssh/ssh_host_rsa_key -N '' -q
# setup mock user
RUN useradd -m -u 1000 -g 135 mockbuild && \
    mkdir -p /home/mockbuild/.ssh && chmod 700 /home/mockbuild /home/mockbuild/.ssh && \
    chown mockbuild:135 /home/mockbuild -R

RUN echo 'config_opts["use_nspawn"] = False' >> /etc/mock/site-defaults.cfg

# do some patch works
RUN patch /usr/lib/python3.9/site-packages/copr_rpmbuild/providers/pypi.py < /pypi.patch && \
    patch /usr/lib/python3.9/site-packages/copr_rpmbuild/providers/rubygems.py < /rubygems.patch && \
    patch /usr/lib/python3.9/site-packages/copr_rpmbuild/providers/base.py < /base.patch
# install pyporter & rubyporter
# using ADD to skip cache
ADD "https://gitee.com/api/v5/repos/openeuler/pyporter/commits?page=1&per_page=1" pyporter_last_commit
RUN git clone https://gitee.com/openeuler/pyporter && cd pyporter && python3 -m pip install -e .

ADD "https://gitee.com/api/v5/repos/openeuler/rubyporter/commits?page=1&per_page=1" rubyporter_last_commit
RUN git clone https://gitee.com/openeuler/rubyporter && cd rubyporter && python3 -m pip install -e .

CMD ["/usr/sbin/sshd", "-D"]
