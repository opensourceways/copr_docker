#!/bin/bash
# Date: 2024-12

# Start executing script at boot, script path: /etc/rc.d/rc.local 
# /etc/rc.d/rc.local << /bin/bash /root/autoRsyncFiles.sh

cat > /root/autoRsyncFiles.sh <<EOF
Copr_target_dir="/copr_docker"

while true
do
    if [ -d "$Copr_target_dir" ]; then
        rm -rf "$Copr_target_dir"
    fi

    git clone https://gh-proxy.test.osinfra.cn/https://github.com/opensourceways/copr_docker.git $Copr_target_dir
      
    if [ $? -eq 0 ];then
        git -C $Copr_target_dir ls-remote --heads origin | grep main >> /tmp/init-script-data.txt
        break
    fi
    sleep 1
done

bash $Copr_target_dir/docker/builder/init-script-for-startup.sh
EOF
