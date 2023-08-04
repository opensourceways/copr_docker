FROM openeuler/openeuler:22.03
LABEL maintainer="infra@openeuler.org"

# TERM is to make the tito work in container, rhbz#1733043
ENV TERM=linux
ENV LANG=en_US.UTF-8
ENV REDIS_HOST=redis

# base packages
RUN set -ex ; \
    dnf -y update && \
    dnf -y install shadow

RUN groupadd -r copr-fe -g 997
RUN useradd -r copr-fe -u 997 -g 997 -d /usr/share/copr/coprs_frontend

# download EUR repo
RUN curl -o /etc/yum.repos.d/eur.repo -L https://eur.openeuler.openatom.cn/coprs/mywaaagh_admin/eur/repo/openeuler-22.03_LTS_SP1/mywaaagh_admin-eur-openeuler-22.03_LTS_SP1.repo

# base packages
RUN set -ex ; \
    dnf -y update && \
    dnf -y install htop \
                   make \
                   which \
                   wget \
                   vim \
                   yum \
                   sudo \
                   python3-alembic \
                   python3-ipdb \
                   python3-anytree \
                   postgresql-server \
                   redis \
                   mock-core-configs \
                   findutils \
                   copr-frontend-1.200 \
                   modulemd-tools \
                   python-pip \
                   patch \
                   git \
    && dnf clean all && rm -rf /var/cache/dnf

COPY files/ /
RUN sed -i 's/User apache/User copr-fe/g' /etc/httpd/conf/httpd.conf
RUN sed -i 's/Group apache/Group copr-fe/g' /etc/httpd/conf/httpd.conf

RUN sed -i 's/ErrorLog.*/ErrorLog "\/dev\/stdout"/g' /etc/httpd/conf/httpd.conf && \
    sed -i 's/CustomLog.*/CustomLog "\/dev\/stdout" combined/g' /etc/httpd/conf/httpd.conf

# We cannot expose privileged port as non-root user
RUN sed -i 's/Listen 80/#Listen 80/g' /etc/httpd/conf/httpd.conf

# Otherwise it is run/httpd.pid in OpenShift, which is outside of
# the copr-fe user permissions
RUN echo "PidFile /var/run/httpd/httpd.pid" >> /etc/httpd/conf/httpd.conf

# Configuration based on environment variables
RUN sed -i "s/REDIS_HOST = \"redis\"/REDIS_HOST = \"${REDIS_HOST}\"/g" /etc/copr/copr.conf

# Some OpenShift shenanigans
# We can't have these directories owned by copr-fe:copr-fe
# because OpenShift runs pod as a semi-randomly generated user
# https://docs.openshift.com/container-platform/4.3/openshift_images/create-images.html#use-uid_create-images
RUN chown -R copr-fe:root \
    /usr/share/copr \
    /var/log/copr-frontend \
    /etc/httpd/ \
    /var/run/httpd/ \
    /var/log/httpd/

# Too bad, Dockerfile can't handle arrays in ARG definitions
# so we need to copy-paste the directories
RUN chmod -R g+rwX \
    /usr/share/copr \
    /var/log/copr-frontend \
    /etc/httpd/ \
    /var/run/httpd/ \
    /var/log/httpd/

# setup for cronjob
RUN echo 'copr-fe ALL=(root) NOPASSWD:/etc/cron.hourly/copr-frontend-optional,/etc/cron.hourly/copr-frontend,/etc/cron.daily/copr-frontend,/etc/cron.daily/copr-frontend-optional' >> /etc/sudoers.d/copr-fe
RUN patch /usr/lib/python3.9/site-packages/copr_common/redis_helpers.py < /redis_helpers.patch
RUN chown -R copr-fe:copr-fe /copr_design
USER copr-fe

# Since home directory for `copr-fe` user is `/usr/share/copr/coprs_frontend`
# and we don't want .bashrc file in there, the bash prompt is `bash-5.0$` which
# looks bad in copy-pasted outputs and tutorials. I borrowed this one from
# /root/.bashrc
ENV PS1="[\u@\h \W]\$ "

# do some patching works
RUN patch /usr/share/copr/coprs_frontend/application < /proxyfix.patch && \
    patch /usr/share/copr/coprs_frontend/coprs/forms.py < /pyporter.patch && \
    cd /usr/share/copr && patch -p2 < /add_openeuler_pkg.patch && \
    patch -p2 < /package_count.patch && \
    patch /usr/share/copr/coprs_frontend/coprs/helpers.py < /helpers.patch && \
    patch -p2 < /oidc_group.patch

RUN cp -r /copr_design/sources/usr / && find /copr_design ! -path /copr_design -exec rm -rf {} \+;
EXPOSE 5000

CMD ["/entrypoint"]
