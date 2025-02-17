config_opts['chroot_setup_cmd'] = 'install yum tar gcc-c++ openEuler-rpm-config openEuler-release which xz sed make bzip2 gzip gcc coreutils unzip shadow-utils diffutils cpio bash gawk rpm-build info patch util-linux findutils grep'
config_opts['dist'] = 'oe2203'  # only useful for --resultdir variable subst
config_opts['releasever'] = '22.03LTS_SP2'
config_opts['package_manager'] = 'dnf'
config_opts['description'] = 'openEuler 22.03 LTS SP2'
config_opts['extra_chroot_dirs'] = [ '/run/lock', ]
config_opts['useradd'] = '/usr/sbin/useradd -o -m -u {{chrootuid}} -g {{chrootgid}} -d {{chroothome}} {{chrootuser}}'
config_opts['bootstrap_image'] = 'docker.io/openeuler/openeuler:22.03-lts-sp2'
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
best=0
install_weak_deps=0
protected_packages=
module_platform_id=platform:oe2203
user_agent={{ user_agent }}

# all openEuler LTS release will continue developing and releasing SPx version
# such as 22.03-LTS -> 22.03-LTS-SP1 -> 22.03-LTS-SP2 ...
# all LTS-SPx is compatible with its LTS release

[OS]
name=OS
baseurl=http://192.168.0.17/openEuler-22.03-LTS-SP2/OS/$basearch/
enabled=1
gpgcheck=1
gpgkey=file:///usr/share/distribution-gpg-keys/openeuler/RPM-GPG-KEY-openEuler-EulerMaker

[everything]
name=everything
baseurl=http://192.168.0.17/openEuler-22.03-LTS-SP2/everything/$basearch/
enabled=1
gpgcheck=1
gpgkey=file:///usr/share/distribution-gpg-keys/openeuler/RPM-GPG-KEY-openEuler-EulerMaker

[EPOL]
name=EPOL
baseurl=http://192.168.0.17/openEuler-22.03-LTS-SP2/EPOL/main/$basearch/
enabled=1
gpgcheck=1
gpgkey=file:///usr/share/distribution-gpg-keys/openeuler/RPM-GPG-KEY-openEuler-EulerMaker

[update]
name=update
baseurl=http://192.168.0.17/openEuler-22.03-LTS-SP2/update/$basearch/
enabled=1
gpgcheck=1
gpgkey=file:///usr/share/distribution-gpg-keys/openeuler/RPM-GPG-KEY-openEuler-EulerMaker

[EPOL-update]
name=EPOL update
baseurl=http://192.168.0.17/openEuler-22.03-LTS-SP2/EPOL/update/main/$basearch/
enabled=1
gpgcheck=1
gpgkey=file:///usr/share/distribution-gpg-keys/openeuler/RPM-GPG-KEY-openEuler-EulerMaker
"""
