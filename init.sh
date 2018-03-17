#!/bin/bash
# init my vms

set -ex
cd /tmp
curl -fsSL get.docker.com -o get-docker.sh
sh get-docker.sh
curl -sSL https://get.daocloud.io/daotools/set_mirror.sh | sh -s http://4816fd23.m.daocloud.io
sudo echo DOCKER_OPTS=\'-H tcp://0.0.0.0:2375 -H unix:///var/run/docker.sock\' >> /etc/default/docker
sudo service docker restart
