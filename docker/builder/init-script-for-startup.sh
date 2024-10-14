#!/bin/bash

yes|cp -r -f /cpor_docker/docker/builder/files/* /

while true; do
  git clone https://gitee.com/openeuler/pyporter /root/pyporter && cd /root/pyporter
  python3 -m pip install -e .
  if [ $? -eq 0 ];then echo "Install pyporter package Successed" >> /root/init-script-date.txt; break; fi
  rm -rf /root/pyporter
done

rm -rf /cpor_docker
rm -rf /root/pyporter
