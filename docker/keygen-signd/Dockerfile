FROM registry.fedoraproject.org/fedora:35
MAINTAINER infra@openeuler.org

# Copy files from the host into the container
COPY files/ /

# Create copr-signer:copr-signer manually, so we can
# be sure that the UID and GID is same on all keygen containers
RUN groupadd -r copr-signer -g 992
RUN useradd -r copr-signer -u 993 -g 992 -d /var/lib/copr-keygen

# Install copr-keygen package
RUN dnf -y update gnupg2 && dnf -y install copr-keygen && dnf clean all

# add tini binary
ENV TINI_VERSION v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini

RUN mkdir -p /var/run/signd

USER copr-signer
ENTRYPOINT ["/tini", "--"]
CMD ["/usr/sbin/signd"]
