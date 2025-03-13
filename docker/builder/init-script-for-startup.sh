#!/bin/bash
# Date: 2024-12

# Install python pyporter application and git clone the latest copr_docker registry
yes|cp -r -f /copr_docker/docker/builder/files/* /
Pyporter_repo_url="https://gitee.com/openeuler/pyporter"

# install git-lfs
cat > /etc/yum.repos.d/eur2.repo <<EOF
[copr:eur.openeuler.openatom.cn:fuyong666:eur]
name=Copr repo for eur owned by fuyong666
baseurl=https://eur.openeuler.openatom.cn/results/fuyong666/eur/openeuler-24.03_LTS_SP1-\$basearch/
type=rpm-md
skip_if_unavailable=True
gpgcheck=1
gpgkey=https://eur.openeuler.openatom.cn/results/fuyong666/eur/pubkey.gpg
repo_gpgcheck=0
enabled=1
enabled_metadata=1
EOF

yum install -y git-lfs

while true
do
    python3 -m pip install git+$Pyporter_repo_url -i  https://mirrors.huaweicloud.com/repository/pypi/simple
    if [ $? -eq 0 ]; then 
        echo "$(date +"%Y-%m-%d %H:%M:%S")  Install Package Successed" >> /tmp/init-script-data.txt
        echo "$(date +"%Y-%m-%d %H:%M:%S")  Install Package Version:  $(su - mockbuild -c "pip list | grep $Pyporter_target_dir")" >> /tmp/init-script-data.txt
        echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++" >> /tmp/init-script-data.txt
        break
    fi
done

rm -rf  /copr_docker
