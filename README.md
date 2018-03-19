### 利用docker-py SDK实现简单多主机容器控制

#### 使用
```
	chmod a+x Docker.py
	# 所有容器
	./Docker.py ps -a
	# 看每个机器的最后一个
	./Docker.py ps -l

	# 创建运行容器, 还可以加--auto_remove参数
	./Docker.py run --host=xs178 --image=nginx:alpine --detach --name=nginx-8 --port="80/tcp:83,443/tcp:448"

	# 操作容器, 支持stop, start, top, stats, restart
	./Docker.py restart --id="xs178:nginx-8"

	# 执行简单命令
	./Docker.py exec --id="xs178:nginx-8" --cmd="ls"

	# 控制指定容器网络，支持: clear, loss, delay, duplicate, corrupt, retrans, rate
	# 分别表示: 清除限制，丢包，延迟, 重复, 坏包, 重发, 限速
	# 参数格式: clear无参数，限速为: "1000 100", 延迟为: "100ms", 其余均为: "10%" 类似
	# 容器限速: 下载500kbit, 上传300kbit
	./Docker.py net --id="xs178:nginx-8" --policy=rate --value="500 300"

	# 延时100ms 上下浮动10ms
	./Docker.py net --id="xs178:nginx-8" --policy=delay --value="100ms 10ms"

	# 丢包20%
	./Docker.py net --id="xs178:nginx-8" --policy=loss --value="20%"

	# 清除策略
	./Docker.py net --id="xs178:nginx-8" --policy=clear

	# 加上--force强制删除容器
	./Docker.py rm --id="xs178:nginx-8" --force
```

#### 初始化工作：
	0. 查资料理思路
	1. 安装虚拟机(我用的之前自己测rabbitmq的ubuntu14.04)
	2. 给虚拟机做公钥信任，因为之后需要远程执行shell命令
	3. scp init脚本到虚拟机，安装docker以及必要的工具wondershaper
	4. 写代码测代码
	5. 写工具配适的命令行参数获取逻辑（待做)

#### 工具思路
	* 远程run/stop/rm/start容器, 直接参照官方文档
	* 远程控制docker容器网络
		参阅资料，linux下有自带tc命令行工具，可以在找到相应容器的虚拟网卡之后，采用远程执行命令，就可以进行限速、丢包、延时、重传等操作;
		之前的是思路是直接在容器里面使用执行tc命令，但是发现有些容器不支持，比如说基于alpine系统的容器，shell是ash，没有tc工具，所以只能从容器所在主机上找到peer netcard进行控制, 用tcpdump、ping和nginx(测限速)工具实测work

* 参考文档及工具:
	* Docker官方文档-Api: <https://docs.docker.com/engine/api/v1.36/#tag/Container>
	* docker-py官方文档: <http://docker-py.readthedocs.io/en/3.1.1/client.html>
	* DockerHub官方镜像仓库: <https://hub.docker.com/explore/>
	* Docker官方文档-网络: <https://docs.docker.com/v1.7/articles/networking/>
	* 容器网络控制思路1: <http://dockone.io/article/1706>
	* 容器网络控制思路2: <http://dockone.io/article/1706>
	* 网络控制问题: <https://stackoverflow.com/questions/42299551/how-to-limit-egress-traffic-of-a-docker-network-with-tc-tbf>
	* 如何找到容器网卡与peer网卡的对应: <https://segmentfault.com/q/1010000012985894/a-1020000012998596>
	* 容器相关问题-容器互通: <https://blog.lab99.org/post/docker-2016-07-14-faq.html#ting-shuo-link-guo-shi-bu-zai-yong-liao-na-rong-qi-hu-lian-fu-wu-fa-xian-zen-me-ban>
	* 容器互联例子: <https://coding.net/u/twang2218/p/docker-lnmp/git?public=true>
	* 容器基础知识: <https://yeasy.gitbooks.io/docker_practice/content/network/linking.html>
	* python SSH第三方库: <https://github.com/paramiko/paramiko>
	* 远程登录相关: <https://github.com/onyxfish/relay/issues/11>
	* 远程登录相关: <https://stackoverflow.com/questions/41718637/unable-to-connect-to-remote-host-using-paramiko>
	* tc Page: <https://wiki.archlinux.org/index.php/advanced_traffic_control>
	* tc命令: <http://blog.csdn.net/weiweicao0429/article/details/17578011>
	* tc QA: <https://serverfault.com/questions/743885/rtnetlink-answers-file-exists-when-using-netem-with-tc>
	* tc QA1: <https://stackoverflow.com/questions/9513981/rtnetlink-answers-no-such-file-or-directory-error>
	* wondershaper简单控制上下行速率: <http://www.cnblogs.com/phpdragon/p/5111680.html>
	* tcpdump: <https://www.cnblogs.com/ggjucheng/archive/2012/01/14/2322659.html>

