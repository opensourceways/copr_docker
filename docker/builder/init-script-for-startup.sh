#!/bin/bash
# Date: 2024-12

# Install python pyporter application and git clone the latest copr_docker registry
yes|cp -r -f /copr_docker/docker/builder/files/* /
REPO_URL="https://gitee.com/openeuler/pyporter"
TARGET_DIR="/pyporter"

while true; do
    if [ -d "$TARGET_DIR" ]; then
        rm -rf "$TARGET_DIR"
    fi

    git clone $REPO_URL $TARGET_DIR
    
    if [ $? -eq 0 ]; then
        break
    fi
    sleep 1
done

chown -R mockbuild. $TARGET_DIR

while true
do
    su - mockbuild -c "python3 -m pip install -e $TARGET_DIR"
    if [ $? -eq 0 ]; then 
        echo "$(date +"%Y-%m-%d %H:%M:%S")  Install Package Successed" >> /tmp/init-script-data.txt
        echo "$(date +"%Y-%m-%d %H:%M:%S")  Install Package Version:  $(su - mockbuild -c "pip list | grep $TARGET_DIR")" >> /tmp/init-script-data.txt
        echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++" >> /tmp/init-script-data.txt
        break
    fi
done

rm -rf  /copr_docker
