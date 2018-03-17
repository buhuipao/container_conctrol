#!/usr/bin/env python
# _*_ coding: utf-8 _*_
#
#   Author:   buhuipao
#   E-mail:   chenhua22@outlook.com
#   Date:     18/03/17 12:34:54
#

import sys
import json
import docker

CLIENT_TIMEOUT = 10
CLIENT_VERSION = "auto"
CONTAINER_OPTIONS = ["stop", "remove", "start", "restart", "stats", "top"]


class DockerCtl(object):
    '''
    用docker-api简单控制操作多主机docker的deamon, 节点信息已写入配置文件
    之后可增加支持一次启动在多个主机启动一组容器(可指定个数)、操作一组容器等
    如果节点很多，因为是网络io, 考虑之后用多线程或协程来并发操作
    '''
    def __init__(self, path):
        self.config_file = path
        self.__load_config()
        self.__prepare_clients()

    def __prepare_clients(self):
        self.__clients = {}
        for node in self.__nodes:
            client = docker.DockerClient(base_url=node["url"],
                                         version=CLIENT_VERSION,
                                         timeout=CLIENT_TIMEOUT)
            self.__clients[node["hostname"]] = client
        if not self.__clients:
            print "Warnnig: nodes is empty"
            sys.exit(1)

    def __load_config(self):
        try:
            with open(self.config_file, 'r') as f:
                self.__config = json.load(f)
                self.__nodes = self.__config["nodes"]
        except Exception as e:
            print "Error: load config file err, {0}".format(e)
            sys.exit(1)

    def __ps(self, client, show_all=False, last=False):
        cs = client.containers.list(all=show_all)
        return cs if not last else cs[-1:]

    def PS(self, show_all=False, last=False):
        for hostname, client in self.__clients.iteritems():
            for c in self.__ps(client, show_all, last):
                attr = c.attrs
                Id = hostname + ":" + attr["Id"][:12]
                Image = attr["Config"]["Image"]
                Command = attr["Config"]["Cmd"]
                Created = attr["Created"]
                Status = attr["State"]["Status"]
                Ports = []
                for k, v in attr["NetworkSettings"]["Ports"].iteritems():
                    if not v:
                        Ports.append("->"+k)
                        continue
                    for i in v:
                        Ports.append(i["HostIp"]+":"+i["HostPort"] + "->" + k)
                Name = attr["Name"]

                print "{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}".format(
                    Id, Image, Command, Created, Status, Ports, Name)

    def RUN(self, host, image, command=None, **kwargs):
        # 指定在一台host运行一个容器
        try:
            c = self.__clients[host].containers.run(image, command, **kwargs)
            if isinstance(c, str) or isinstance(c, unicode):
                print "Create attach container success!"
                print c
            else:
                print "Create detach container success!"
                print c.logs()
        except Exception as e:
            print "Error: run container err, {0}", e
            sys.exit(1)

    def find_container(self, id_or_name):
        # 根据id或name找到目标容器, 可供stop, start, rm方法用
        hostname_id = id_or_name.strip().split(":")
        if len(hostname_id) != 2 or hostname_id[0] not in self.__clients:
            print "Error: invaild container_id!"
            sys.exit(0)
        client = self.__clients[hostname_id[0]]
        found, dest = False, []
        for c in client.containers.list(all=True):
            if c.attrs["Name"].strip("/") == hostname_id[1].strip("/") or \
                    c.attrs["Id"].startswith(hostname_id[1]):
                dest.append(c)
                found = True
        if not found:
            print "Warnning: not find container by name or id, do nothing"
            sys.exit(0)
        elif len(dest) != 1:
            print "Please enter longer ID or name, do nothing"
            sys.exit(0)
        else:
            return dest[0]

    def OPTION(self, method, id_or_name, **kwargs):
        if method == "rm":
            method = "remove"
        if method not in CONTAINER_OPTIONS:
            print "Warnning: unsupported method"
            sys.exit(0)
        dest = self.find_container(id_or_name)
        operate = getattr(dest, method)
        try:
            result = operate(**kwargs)
            print result
            print "Success {0} container {1}".format(method, id_or_name)
        except Exception as e:
            print "Error: {0} {1}, {2}".format(method, id_or_name, e)
            sys.exit(1)
