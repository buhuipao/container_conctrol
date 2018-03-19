#!/usr/bin/env python
# _*_ coding: utf-8 _*_
#
#   Author:   buhuipao
#   E-mail:   chenhua22@outlook.com
#   Date:     18/03/19 06:56:55
#

import argparse
import sys
from container_ctl import DockerCtl
import container_ctl
from ipdb import set_trace


def parse_args():
    '''参数解析
    '''
    parser = argparse.ArgumentParser(description='control you containers')
    parser.add_argument(
        "option",
        help="choose your options, [ps|run|stop|top|start|rm|restart|net]")

    # ps args
    parser.add_argument(
        '-a', required=False, action='store_true', help='ps all containers')
    parser.add_argument(
        '-l', required=False, action='store_true', help='ps last container')

    # run container args
    parser.add_argument(
        '--name', required=False, help='run container with a name')
    parser.add_argument(
        '--host', required=False, help='run container in which host')
    parser.add_argument(
        '--image', required=False, help='run with which image')
    parser.add_argument(
        '--detach', required=False, action='store_true',
        help='run a detach or attach container')
    parser.add_argument(
        '--auto_remove', required=False, action='store_true',
        help='run a container remove if exit')
    parser.add_argument(
        '--command', required=False, help='run a container with cmd')
    parser.add_argument(
        '--ports', required=False,
        help='expose ports, <container_port>/<protocol>:<host_port>,<conta...')

    parser.add_argument(
        '--id', required=False,
        help='dest option container, like <host_name>:<short_id_or_name>')

    # exec cmd args
    parser.add_argument(
        '--cmd', required=False, help='run a container with cmd')

    # rm, stop, restart, start, stats, top args
    parser.add_argument(
        '--force', required=False, action='store_true', help='force operate')

    # net_control args
    parser.add_argument(
        '--clear', required=False,
        help='clear network limit policy, example: 30%')
    parser.add_argument(
        '--loss', required=False,
        help='loss package percent, example: 30%')
    parser.add_argument(
        '--delay', required=False,
        help='netem delay xx/ms, like 100ms 10ms, meaning <basic> <floating>')
    parser.add_argument(
        '--duplicate', required=False,
        help='duplicate package, example: 10%')
    parser.add_argument(
        '--corrupt', required=False,
        help='corrupt package, example: 0.1%')
    parser.add_argument(
        '--retrans', required=False,
        help='miss package retrans, example: 20%')
    parser.add_argument(
        '--rate', required=False,
        help='limit <download> <upload> rate(Kpbs), example: 800 400')
    parser.add_argument(
        '--policy', required=False,
        help='can be [clear|loss|delay|duplicate|corrupt|retans|rate]')
    parser.add_argument(
        '--value', required=False,
        help='like [20%, 100ms 10ms, 800 400] depend on your select policy')
    args = parser.parse_args()
    return args


def main():
    '''控制容器
    '''
    args = parse_args()
    kwargs = vars(args)
    empty_args = [i for i in kwargs if not kwargs[i]]
    ctl = DockerCtl("config.json")

    option = args.option
    if option == "ps":
        ctl.PS(show_all=args.a, last=args.l)
    elif option == "run":
        # 先处理端口映射参数
        if kwargs["ports"]:
            ports = {}
            for port in kwargs["ports"].split(","):
                c, h = port.split(':')
                ports[c] = h
        kwargs["ports"] = ports

        host, image, command = args.host, args.image, args.command
        map(lambda i: kwargs.pop(i),
            set(["option", "host", "image", "command"] + empty_args))
        ctl.RUN(host, image, command, **kwargs)
    elif option in container_ctl.CONTAINER_OPTIONS:
        Id = args.id
        map(lambda i: kwargs.pop(i), set(["option", "id"] + empty_args))
        ctl.OPTION(option, Id, **kwargs)
    elif option == "exec":
        Id, cmd = args.id, args.cmd
        map(lambda i: kwargs.pop(i), set(["option", "id", "cmd"] + empty_args))
        ctl.RUNCMD(Id, cmd, **kwargs)
    elif option == "net":
        ctl.net_control(args.id, args.policy, args.value)
    else:
        print "Warnnging: invaild option"
        sys.exit(1)

if __name__ == '__main__':
    main()
