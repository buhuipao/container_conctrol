### 利用docker-py SDK实现简单多主机容器控制

* 参考文档及工具:
	`Docker官方文档-Api`: <https://docs.docker.com/engine/api/v1.36/#tag/Container>
	`docker-py官方文档`: <http://docker-py.readthedocs.io/en/3.1.1/client.html>
	`DockerHub官方镜像仓库`: <https://hub.docker.com/explore/>
	`Docker官方文档-网络`: <https://docs.docker.com/v1.7/articles/networking/>

	`容器网络结构图`: 
	`容器网络控制思路1`: <http://dockone.io/article/1706>
	`容器网络控制思路2`: <http://dockone.io/article/1706>
	`网络控制问题`: <https://stackoverflow.com/questions/42299551/how-to-limit-egress-traffic-of-a-docker-network-with-tc-tbf>

	`如何找到容器网卡与peer网卡的对应`: <https://segmentfault.com/q/1010000012985894/a-1020000012998596>
	`容器相关问题-容器互通`: <https://blog.lab99.org/post/docker-2016-07-14-faq.html#ting-shuo-link-guo-shi-bu-zai-yong-liao-na-rong-qi-hu-lian-fu-wu-fa-xian-zen-me-ban>
	`容器互联例子`: <https://coding.net/u/twang2218/p/docker-lnmp/git?public=true>

	`容器基础知识`: <https://yeasy.gitbooks.io/docker_practice/content/network/linking.html>
