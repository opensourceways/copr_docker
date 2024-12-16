#!/bin/bash
# Date: 2024-12

# Install python pyporter application and git clone the latest copr_docker registry
yes|cp -r -f /copr_docker/docker/builder/files/* /
Pyporter_repo_url="https://gitee.com/openeuler/pyporter"
Pyporter_target_dir="/pyporter"

while true; do
    if [ -d "$Pyporter_target_dir" ]; then
        rm -rf "$Pyporter_target_dir"
    fi

    git clone $Pyporter_repo_url $Pyporter_target_dir
    
    if [ $? -eq 0 ]; then
        break
    fi
    sleep 1
done

chown -R mockbuild. $Pyporter_target_dir

while true
do
    su - mockbuild -c "python3 -m pip install -e $Pyporter_target_dir"
    if [ $? -eq 0 ]; then 
        echo "$(date +"%Y-%m-%d %H:%M:%S")  Install Package Successed" >> /tmp/init-script-data.txt
        echo "$(date +"%Y-%m-%d %H:%M:%S")  Install Package Version:  $(su - mockbuild -c "pip list | grep $Pyporter_target_dir")" >> /tmp/init-script-data.txt
        echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++" >> /tmp/init-script-data.txt
        break
    fi
done

rm -rf  /copr_docker
