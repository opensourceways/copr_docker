config_opts['chroot_setup_cmd'] = 'install tar gcc-c++ openEuler-rpm-config openEuler-release which xz sed make bzip2 gzip gcc coreutils unzip shadow-utils diffutils cpio bash gawk rpm-build info patch util-linux findutils grep procps-ng bc'
config_opts['dist'] = 'oe1'  # only useful for --resultdir variable subst
config_opts['releasever'] = '20.03-LTS'
config_opts['package_manager'] = 'dnf'
config_opts['description'] = 'openEuler 20.03 LTS'
config_opts['extra_chroot_dirs'] = [ '/run/lock', ]
config_opts['useradd'] = '/usr/sbin/useradd -o -m -u {{chrootuid}} -g {{chrootgid}} -d {{chroothome}} {{chrootuser}}'
config_opts['bootstrap_image'] = 'docker.io/openeuler/openeuler:20.03'
config_opts['nosync'] = True
config_opts['nosync_force'] = True
config_opts['macros']['%_smp_ncpus_max'] = '4'
config_opts['dnf.conf'] = """
[main]
keepcache=1
debuglevel=2
reposdir=/dev/null
logfile=/var/log/yum.log
retries=20
obsoletes=1
gpgcheck=0
assumeyes=1
syslog_ident=mock
syslog_device=
metadata_expire=0
mdpolicy=group:primary
best=1
install_weak_deps=0
protected_packages=
module_platform_id=platform:oe2003
user_agent={{ user_agent }}

[OS]
name=OS
baseurl=http://mirrors.tuna.tsinghua.edu.cn/openeuler/openEuler-20.03-LTS/OS/$basearch/
enabled=1
gpgcheck=1
gpgkey=file:///usr/share/distribution-gpg-keys/openeuler/RPM-GPG-KEY-openEuler

[everything]
name=everything
baseurl=http://mirrors.tuna.tsinghua.edu.cn/openeuler/openEuler-20.03-LTS/everything/$basearch/
enabled=1
gpgcheck=1
gpgkey=file:///usr/share/distribution-gpg-keys/openeuler/RPM-GPG-KEY-openEuler

[EPOL]
name=EPOL
baseurl=https://mirrors.tuna.tsinghua.edu.cn/openeuler/openEuler-20.03-LTS/EPOL/$basearch/
enabled=1
gpgcheck=1
gpgkey=file:///usr/share/distribution-gpg-keys/openeuler/RPM-GPG-KEY-openEuler

[debuginfo]
name=debuginfo
baseurl=http://mirrors.tuna.tsinghua.edu.cn/openeuler/openEuler-20.03-LTS/debuginfo/$basearch/
enabled=0
gpgcheck=1
gpgkey=file:///usr/share/distribution-gpg-keys/openeuler/RPM-GPG-KEY-openEuler

[source]
name=source
baseurl=http://mirrors.tuna.tsinghua.edu.cn/openeuler/openEuler-20.03-LTS/source/
enabled=0
gpgcheck=1
gpgkey=file:///usr/share/distribution-gpg-keys/openeuler/RPM-GPG-KEY-openEuler


[update]
name=update
baseurl=http://mirrors.tuna.tsinghua.edu.cn/openeuler/openEuler-20.03-LTS/update/$basearch/
enabled=1
gpgcheck=1
gpgkey=file:///usr/share/distribution-gpg-keys/openeuler/RPM-GPG-KEY-openEuler
"""
