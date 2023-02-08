FROM registry.fedoraproject.org/fedora:37
LABEL maintainer="infra@openeuler.org"

ARG ADDITIONAL_COPR_REPOSITORIES="@copr/copr-dev"

# TERM is to make the tito work in container, rhbz#1733043
ENV TERM=linux
ENV PYTHONPATH=/usr/share/copr/

# base packages
RUN set -ex ; \
    test -z "${ADDITIONAL_COPR_REPOSITORIES}" \
        || dnf -y install dnf-plugins-core \
        && for repo in $ADDITIONAL_COPR_REPOSITORIES ; do dnf -y copr enable $repo; done ; \
    dnf -y update && \
    dnf -y install htop \
                   which \
                   wget \
                   vim \
                   cgit \
                   python3-rpkg \
                   python3-ipdb \
                   tini \
                   && \
    dnf -y install copr-dist-git && \
    dnf clean all

RUN rm /etc/httpd/conf.d/ssl.conf

RUN echo "AliasMatch \"/repo(/.*)/md5(/.*)\" \"/var/lib/dist-git/cache/lookaside\\$1\\$2\"" >> /etc/httpd/conf.d/dist-git/lookaside-copr.conf && \
    echo "Alias /repo/ /var/lib/dist-git/cache/lookaside/" >>  /etc/httpd/conf.d/dist-git/lookaside-copr.conf

RUN sed -i 's/Listen 80/Listen 5001/' /etc/httpd/conf/httpd.conf \
    sed -i 's/ErrorLog.*/ErrorLog "\/dev\/stdout"/g' /etc/httpd/conf/httpd.conf \
    sed -i 's/CustomLog.*/CustomLog "\/dev\/stdout" combined/g' /etc/httpd/conf/httpd.conf

RUN mkdir /tmp/copr-dist-git /var/log/copr-dist-git
RUN chown copr-dist-git:packager /tmp/copr-dist-git

# copy filesystem setup and setup ownership and permissions
COPY files/ /
RUN chmod 644 /etc/copr/copr-dist-git.conf && chmod 755 /copr-dist-git-assure-perm

RUN echo " [user]" >> /home/copr-dist-git/.gitconfig && \
    echo " email = infra@openeuler.org" >> /home/copr-dist-git/.gitconfig && \
    echo " name = Copr dist git" >> /home/copr-dist-git/.gitconfig && \
    chown copr-dist-git:copr-dist-git /home/copr-dist-git/.gitconfig /var/log/copr-dist-git

RUN sed -i "s/^cache-size.*//" /etc/cgitrc
RUN echo 'scan-path=/var/lib/dist-git/git/rpms' | tee -a /etc/cgitrc

RUN directories="/etc/httpd /var/run/httpd /var/log/httpd /var/lib/dist-git /run/lock" ; \
    chown -R copr-dist-git:root $directories && \
    chmod -R g+rwX $directories

RUN echo "copr-dist-git ALL = (root) NOPASSWD: /copr-dist-git-assure-perm" >> /etc/sudoers.d/copr-dist-git

USER copr-dist-git

RUN ln -sf /proc/self/fd/1 /var/log/copr-dist-git/main.log

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["bash", "-c", "mkdir -p /var/lib/dist-git/cache /var/lib/dist-git/git && sudo /copr-dist-git-assure-perm && exec /usr/bin/copr-run-dispatcher imports"]
