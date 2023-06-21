config_opts['chroot_setup_cmd'] = 'install yum tar gcc-c++ openEuler-rpm-config openEuler-release which xz sed make bzip2 gzip gcc coreutils unzip shadow-utils diffutils cpio bash gawk rpm-build info patch util-linux findutils grep procps-ng bc'
config_opts['dist'] = 'oe1'  # only useful for --resultdir variable subst
config_opts['releasever'] = '20.03LTS_SP2'
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
metalink=https://mirrors.openeuler.org/metalink?repo=$releasever/OS&arch=$basearch
baseurl=https://mirrors.163.com/openeuler/openEuler-20.03-LTS-SP2/OS/$basearch/
baseurl=https://mirrors.pku.edu.cn/openeuler/openEuler-20.03-LTS-SP2/OS/$basearch/
baseurl=https://mirrors.nju.edu.cn/openeuler/openEuler-20.03-LTS-SP2/OS/$basearch/
enabled=1
gpgcheck=1
gpgkey=file:///usr/share/distribution-gpg-keys/openeuler/RPM-GPG-KEY-openEuler

[everything]
name=everything
metalink=https://mirrors.openeuler.org/metalink?repo=$releasever/everything&arch=$basearch
baseurl=https://mirrors.163.com/openeuler/openEuler-20.03-LTS-SP2/everything/$basearch/
baseurl=https://mirrors.pku.edu.cn/openeuler/openEuler-20.03-LTS-SP2/everything/$basearch/
baseurl=https://mirrors.nju.edu.cn/openeuler/openEuler-20.03-LTS-SP2/everything/$basearch/
enabled=1
gpgcheck=1
gpgkey=file:///usr/share/distribution-gpg-keys/openeuler/RPM-GPG-KEY-openEuler

[EPOL]
name=EPOL
metalink=https://mirrors.openeuler.org/metalink?repo=$releasever/EPOL/main&arch=$basearch
baseurl=https://mirrors.163.com/openeuler/openEuler-20.03-LTS-SP2/EPOL/main/$basearch/
baseurl=https://mirrors.pku.edu.cn/openeuler/openEuler-20.03-LTS-SP2/EPOL/main/$basearch/
baseurl=https://mirrors.nju.edu.cn/openeuler/openEuler-20.03-LTS-SP2/EPOL/main/$basearch/
enabled=1
gpgcheck=1
gpgkey=file:///usr/share/distribution-gpg-keys/openeuler/RPM-GPG-KEY-openEuler

[update]
name=update
metalink=https://mirrors.openeuler.org/metalink?repo=$releasever/update&arch=$basearch
baseurl=https://mirrors.163.com/openeuler/openEuler-20.03-LTS-SP2/update/$basearch/
baseurl=https://mirrors.pku.edu.cn/openeuler/openEuler-20.03-LTS-SP2/update/$basearch/
baseurl=https://mirrors.nju.edu.cn/openeuler/openEuler-20.03-LTS-SP2/update/$basearch/
enabled=1
gpgcheck=1
gpgkey=file:///usr/share/distribution-gpg-keys/openeuler/RPM-GPG-KEY-openEuler

[EPOL-update]
name=EPOL update
metalink=https://mirrors.openeuler.org/metalink?repo=$releasever/EPOL/update/main&arch=$basearch
baseurl=https://mirrors.163.com/openeuler/openEuler-20.03-LTS-SP2/EPOL/update/main/$basearch/
baseurl=https://mirrors.pku.edu.cn/openeuler/openEuler-20.03-LTS-SP2/EPOL/update/main/$basearch/
baseurl=https://mirrors.nju.edu.cn/openeuler/openEuler-20.03-LTS-SP2/EPOL/update/main/$basearch/
enabled=1
gpgcheck=1
gpgkey=file:///usr/share/distribution-gpg-keys/openeuler/RPM-GPG-KEY-openEuler
"""
