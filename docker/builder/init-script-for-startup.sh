#!/bin/bash
# Date: 2024-12

# Install python pyporter application and git clone the latest copr_docker registry
yes|cp -r -f /copr_docker/docker/builder/files/* /
Pyporter_repo_url="https://gitee.com/openeuler/pyporter"

while true
do
    python3 -m pip install git+$Pyporter_repo_url -i https://mirrors.huaweicloud.com/repository/pypi/simple
    if [ $? -eq 0 ]; then 
        echo "$(date +"%Y-%m-%d %H:%M:%S")  Install Package Successed" >> /tmp/init-script-data.txt
        echo "$(date +"%Y-%m-%d %H:%M:%S")  Install Package Version:  $(pip list | grep pyporter)" >> /tmp/init-script-data.txt
        echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++" >> /tmp/init-script-data.txt
        break
    fi
done

rm -rf  /copr_docker
