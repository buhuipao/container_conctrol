#!/usr/bin/env python
# _*_ coding: utf-8 _*_
#
#   Author:   buhuipao
#   E-mail:   chenhua22@outlook.com
#   Date:     18/03/17 15:25:49
#


from container_ctl import DockerCtl

ctl = DockerCtl("config.json")


def test_PS():
    ctl.PS()


def test_RUN():
    ctl.RUN("xs178", "nginx:alpine", "echo ok",
            name="nginx-6", auto_remove=True,
            ports={"80/tcp": 86}, detach=False)


def test_OPTION():
    # c_id in ["x_xx", "xs178:nginxNotExsit", "xs178:nginx-4"]:
    # methods = ["stop", "remove", "start", "restart", "stats", "rm"]
    ctl.OPTION("stats", "xs178:nginx-1")


def test_RUNCMD():
    # ls, pwd
    ctl.RUNCMD("xs178:nginx-4", "ls -al /root")
    ctl.RUNCMD("xs178:nginx-4", ["cd", "/tmp", "&&", "pwd", "&&", "ls"])
    ctl.RUNCMD("xs178:nginx-4", ["eth"])


def main():
    test_PS()
    test_OPTION()
    test_PS()

if __name__ == "__main__":
    main()
