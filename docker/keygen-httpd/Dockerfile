FROM openeuler/openeuler:22.03
LABEL maintainer="infra@openeuler.org"


# Create copr-signer:copr-signer manually, so we can
# be sure that the UID and GID is same on all keygen containers
RUN groupadd -r copr-signer -g 992
RUN useradd -r copr-signer -u 993 -g 992 -d /var/lib/copr-keygen

# download EUR repo
RUN curl -o /etc/yum.repos.d/eur.repo -L https://eur.openeuler.openatom.cn/coprs/mywaaagh_admin/eur/repo/openeuler-22.03_LTS_SP1/mywaaagh_admin-eur-openeuler-22.03_LTS_SP1.repo

# base packages
RUN dnf -y update && \
    dnf -y install htop \
                   httpd \
                   make \
                   which \
                   wget \
                   vim \
                   yum \
                   sudo \
                   supervisor \
                   python3-alembic \
                   postgresql-server \
                   redis \
                   && \
    dnf -y install copr-keygen-1.88 && \
    dnf clean all && rm -rf /var/cache/dnf

# system setup for copr-keygen
RUN mkdir /var/log/uwsgi /var/run/uwsgi && \
    chown apache:apache /var/log/uwsgi && \
    chmod 775 /var/log/uwsgi && \
    chown apache:apache /var/run/uwsgi && \
    chmod 775 /var/run/uwsgi && \
    usermod copr-signer -G apache

# Copy files from the host into the container
COPY files/ /

RUN sed -i 's/Listen 80/#Listen 80/g' /etc/httpd/conf/httpd.conf

CMD ["/entrypoint"]
