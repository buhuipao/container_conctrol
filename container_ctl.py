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
import paramiko
from ipdb import set_trace

CLIENT_TIMEOUT = 10
CLIENT_VERSION = "auto"
CONTAINER_OPTIONS = ["stop", "remove", "start", "restart", "stats", "top"]
IP_A = "ip a"
# TC_NOT_FOUND_ERR = "RTNETLINK answers: No such file or directory\n"


class DockerCtl(object):
    '''
    用docker-api简单控制操作多主机docker的deamon, 节点信息已写入配置文件
    之后可增加支持一次启动在多个主机启动一组容器(可指定个数)、操作一组容器等
    如果节点很多，因为是网络io, 考虑之后用多线程或协程来并发操作
    '''
    def __init__(self, path):
        self.config_file = path
        self.__sshs = {}
        # 网络控制模板
        self.__net_control = {
            "clear": "tc qdisc del dev {0} root || wondershaper clear {0}",
            "loss": "tc qdisc add dev {0} root netem loss {1}",
            "delay": "tc qdisc add dev {0} root netem delay {1}",
            "duplicate": "tc qdisc add dev {0} root netem duplicate {1}",
            "corrupt": "tc qdisc add dev {0} root netem corrupt {1}",
            "retrans": "tc qdisc add dev {0} root netem delay 10ms reorder {1}",
            # netcard，down, upload
            "limit": "wondershaper {0} {1}"}
        #  "tc qdisc add dev {0} root tbf rate {1}kbit latency 50ms burst {2}"

        self.__load_config()
        self.__prepare_clients()

    def __prepare_clients(self):
        self.__clients = {}
        for node in self.__nodes.values():
            client = docker.DockerClient(base_url=node["url"],
                                         version=CLIENT_VERSION,
                                         timeout=CLIENT_TIMEOUT)
            self.__clients[node["hostname"]] = client
        if not self.__clients:
            print("Warnnig: nodes is empty")
            sys.exit(1)

    def __load_config(self):
        try:
            with open(self.config_file, 'r') as f:
                self.__config = json.load(f)
                self.__nodes = {}
                for node in self.__config["nodes"]:
                    self.__nodes[node["hostname"]] = node
        except Exception as e:
            print("Error: load config file err, {0}".format(e))
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

                print("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}".format(
                    Id, Image, Command, Created, Status, Ports, Name))

    def RUN(self, host, image, command=None, **kwargs):
        # 指定在一台host运行一个容器
        try:
            c = self.__clients[host].containers.run(image, command, **kwargs)
            if isinstance(c, str) or isinstance(c, unicode):
                print("Create attach container success!")
                print(c)
            else:
                print("Create detach container success!")
                print(c.logs())
        except Exception as e:
            print("Error: run container err, {0}".format(e))
            sys.exit(1)

    def find_container(self, id_or_name):
        # 根据id或name找到目标容器, 可供stop, start, rm, exec等方法用
        hostname_id = id_or_name.strip().split(":")
        if len(hostname_id) != 2 or hostname_id[0] not in self.__clients:
            print("Warnnig: invaild container_id or name!")
            raise ValueError("Invaild container_id or name")

        client = self.__clients[hostname_id[0]]
        found, dest = False, []
        for c in client.containers.list(all=True):
            if c.attrs["Name"].strip("/") == hostname_id[1].strip("/") or \
                    c.attrs["Id"].startswith(hostname_id[1]):
                dest.append(c)
                found = True

        if not found:
            print(
                "Warnning: not find container by name or id, do nothing")
            raise ValueError("Not found container_id or name")
        elif len(dest) != 1:
            print("Please enter longer ID or name, do nothing")
            raise ValueError("Too short container_id or name")
        else:
            return dest[0]

    def OPTION(self, method, id_or_name, **kwargs):
        if method == "rm":
            method = "remove"
        if method not in CONTAINER_OPTIONS:
            print("Warnning: unsupported method")
            sys.exit(0)
        dest = self.find_container(id_or_name)
        operate = getattr(dest, method)
        try:
            result = operate(**kwargs)
            print(result)
            print("Success {0} container {1}".format(method, id_or_name))
        except Exception as e:
            print("Error: {0} {1}, {2}".format(method, id_or_name, e))
            sys.exit(1)

    def RUNCMD(self, id_or_name, cmd, **kwargs):
        dest = self.find_container(id_or_name)
        try:
            exit_code, output = dest.exec_run(cmd, **kwargs)
            if exit_code == 0:
                print("Cmd exec success")
            else:
                print("Cmd exec failed")
            print(output)
            return exit_code, output
        except Exception as e:
            print("Error: exec {0} err, {1}".format(cmd, e))
            raise

    def gen_host_connection(self, host_ip, username="root"):
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host_ip, 22, username)
        return ssh

    def find_peer_netcard(self, id_or_name):
        # 从容器中先取出iflink, 然后去host里面去找相应的虚拟网卡
        try:
            code, output = self.RUNCMD(id_or_name, IP_A)
            if code != 0:
                raise
        except:
            print(
                "Error: get container {0} netcard iflink failed".format(
                    id_or_name))
            raise
        for line in output.strip().split("\n"):
            if line.find("eth0@") != -1:
                return int(line.split(":")[1].split("if")[-1])

    def exec_cmd(self, host_ip, cmd):
        try:
            if host_ip not in self.__sshs:
                ssh = self.gen_host_connection(host_ip)
                print("Connected {0} success".format(host_ip))
                # 此处保存下ssh之后可以执行网络控制时使用
                self.__sshs[host_ip] = ssh
            else:
                ssh = self.__sshs[host_ip]
        except Exception as e:
            print("Error: connect {0} failed, {1}".format(host_ip, e))
            raise
        return ssh.exec_command(cmd)

    def get_container_virtual_netcard(self, id_or_name):
        netcard_index = self.find_peer_netcard(id_or_name)
        host_ip = self.find_container_host_ip(id_or_name)
        stdin, stdout, stderr = self.exec_cmd(host_ip, IP_A)
        if stderr.readlines():
            print(
                "Error: exec {0} failed, {1}".format(IP_A, stderr.readlines()))
            raise RuntimeError(stderr.readlines())
        netcard = ""
        for line in stdout.readlines():
            if line.find(str(netcard_index)+": veth") != -1:
                netcard = line.strip("\n").split("@")[0].split()[-1]
                break
        return netcard

    def find_container_host_ip(self, id_or_name):
        hostname_id = id_or_name.split(":")
        if len(hostname_id) != 2 or hostname_id[0] not in self.__nodes:
            print("Error: invaild container_id or name!")
            raise ValueError("Error: invaild container_id or name!")
        return self.__nodes[hostname_id[0]]["url"].split("//")[-1].split(":")[0]

    def net_control(self, id_or_name, option, args):
        # 容器网络控制的执行入口
        host_ip = self.find_container_host_ip(id_or_name)
        if option not in self.__net_control:
            print(
                "Warnnig: invaild net_control option {0}".format(option))
            return
        virtual_netcard = self.get_container_virtual_netcard(id_or_name)
        if not virtual_netcard:
            print("Error: invaild virtual netcard, do nothing")
            return
        # clear before option
        cmd1 = self.__net_control["clear"].format(virtual_netcard, args)
        cmd2 = self.__net_control[option].format(virtual_netcard, args)

        try:
            for cmd in (cmd1, cmd2):
                stdin, stdout, stderr = self.exec_cmd(host_ip, cmd)
                # 如果是清除网络控制命令则忽略错误
                if cmd.find("wondershaper clear") == -1 and stderr.readlines():
                    print(stderr.readlines())
            print("{0} {1} --> {2} success".format(option, args, id_or_name))
        except Exception as e:
            print(
                "Error: {0} {1} network failed, {2}".format(
                    option, id_or_name, e))
            raise RuntimeError(e)
