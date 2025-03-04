FROM openeuler/openeuler:24.03-lts
LABEL maintainer="infra@openeuler.org"

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
