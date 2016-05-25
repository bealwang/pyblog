title:linux机群系统DIY
tags:python,静态,博客,seo,代码高亮      
showName:pc-1

##情景
没有云平台?没有昂贵,完备的并行自动化部署工具?只有计算机硬件设备?但是还是任性的想优雅的使用并行环境?
下面就让我们一起愉快的经历DIY并行环境的历程吧...
{{ alert("注意以下的操作在所有节点上均需要执行", "danger") }}

##操作系统的安装
这里主要有几款常见的linux操作系统:
 - Redhat Linux
 - SuSE Linux
 - Debian GNU/Linux

前两个版本具有可管理性强和用户界面友好等优点,后一个具有可裁剪性强的优点,按照需求任意选择一款即可.
##操作系统配置
###主机名配置
通过修改{{ text("/etc/sysconfig/network", "success") }}文件中的{{ text("HOSTNAME", "success") }}字段
可以修改主机名,但是需要重新启动系统生效.
本博客假设使用的主机名和ip分别是:    
  vm-1-1         10.0.0.11   (主节点)    
  vm-1-2         10.0.0.12    
  vm-1-3         10.0.0.13    
  vm-1-4         10.0.0.14    
###网络配置
1. 修改{{ text("/etc/hosts", "success") }}文件中的主机列表,将所有的计算节点名以及ip信息写入,形式如下:    
10.0.0.11    vm-1-1    
10.0.0.12    vm-1-2    
10.0.0.13    vm-1-3    
10.0.0.14    vm-1-4    
2. 配置防火墙
可以使用如下命令查看当前防火墙设置:
```shell
iptables -L
```
配置防火墙,使得远程用户可通过ssh正常访问,命令如下:
```shell
iptables -A INPUT -p tcp -dport 22 -j A:
```
3. 用ping命令检查节点间的互通状态:
{{ img("./img/1.jpg", "检查节点互通", "图片挂了", "网络配置") }}
确保节点之间两两互通,对于不能互通的节点对,可以按照如下命令格式添加路由:    
route add 网段地址 Mask 子网掩码 网关地址
```shell
route add 172.21.0.0 Mask 255.255.0.0 172.21.0.1
```

###新增用户
可以使用命令adduser命令增加并行计算用户,格式如下:
```shell
adduser mpiuser
```

###配置SSH(Secure SHell)服务
我们选用linux平台广泛使用的OpenSSH,它由服务器软件包openssh-server和客户端程序openssh-clientis组成,
默认情况下,两者已经安装在你的系统中了.
1. 查看方式:
```shell
rpm -q openssh-server
rpm -q openssh-clients
```
2. 启动和查询SSH服务
一般linux默认开机启动SSH服务,所以大家可以直接使用可使用{{ text("ntsysv", "success") }}命令,将SSH服
务设置为开机自启动服务    
也可以使用如下命令启动/重启/停止/查询SSH服务
```shell
service sshd start/restart/stop/status
```
3. 配置节点之间无密码ssh互通
相应的示例命令如下:
```shell
ssh-keygen -t rsa -C "youremail@sina.com"
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
ssh-copy-id mpiuser@vm-1-1
```
{{ alert("注意这个操作在所有节点上的mpiuser用户下均需执行,直到计算节点-->主节点以及主节点-->计算节点均可互通", "warning") }}

到此为止,组成并行计算环境的所有计算节点上均具有相同的主机列表,节点间均可互通.
##MPICH的安装与配置
{{ alert("注意以下的操作在所有节点上均需要执行", "danger") }}

###MPI的安装
1. 下载MPICH软件安装包mpich2    {{ text("1.2.1p1.tar.gz", "success") }}
以mpiuser用户解压软件包,创建安装路径,配置安装路径,编译,安装.命令如下:
```shell
tar zxvf mpich2-1.2.1p1.tar.gz
cd mpich2-1.2.1p1
mkdir /home/mpiuser/mpi2-1.2.1p1_install
./configure –prefix=/home/mpiuser/mpi2-1.2.1p1_install
make && make install
```
2. 设置环境变量
在{{ text("/home/mpiuser/.bashrc", "success") }}文件中添加如下语句:
```shell
export PATH=/home/mpiuser/mpi2-1.2.1p1_install/bin:$PATH
```
运行{{ text("source", "success") }}命令使我们的修改生效.
3. 检查安装是否成功
{{ img("./img/2.jpg", "查看安装是否成功", "图片挂了", "安装mpi") }}

###MPI的配置
1. 配置mdp.conf文件
在mpiuser的主目录下创建文件.mdp.conf    
编辑.mdp.conf文件,添加语句:{{ text("secretword=111111", "success") }}    
修改.mdp.conf文件的访问权限:
```shell
chmod 644 .mdp.conf
```
2. 启动mdp守护进程
在mpiuser的主目录下,创建mpd.hosts文件,将计算节点名称列表填入,本博客使用的是vm-1-2~vm-1-4.    
启动各节点上的mdp
```shell
mdpboot -n 启动个数 -f ~/mdp.hosts
```
检查是否启动正常:
{{ img("./img/3.jpg", "检查mdp启动情况", "图片挂了", "启动mdp") }}
mdp的关闭命令是{{ text("mdpallexit", "success") }}

###MPI的使用
我们只关心并行环境的搭建,对于MPI的使用,咱们就一带而过啦.
{{ img("./img/4.jpg", "mpi的使用", "图片挂了", "mpi的使用") }}

##NFS
网络文件系统NFS(Network File System)是{{ text("UNIX\Linux", "success") }}系统支持的一种网络文件服务.
通过NFS,网络中的计算机可以发布共享信息,远程客户端能够像使用本地文件一样访问该共享资源.
{{ img("./img/5.png", "NFS", "图片挂了", "NFS") }}

它有如下优点:
 - 节约磁盘空间
 - 节约硬件设备
 - 共享用户和应用程序目录

##NFS的安装
相关rpm软件包:    
nfs-utils-*.rpm:NFS服务主程序包    
Portmap-*.rpm:记录服务的端口映射信息    
安装命令:
```shell
rpm -ivh nfs-utils-*.rpm
```

##NFS服务端的配置
1. 配置{{ text("/etc/exports", "success") }}文件:
 - 用于定义需要共享的目录，以及访问对象的控制
 - 默认情况下，该文件内容为空，即不共享任何目录
 - 当需要共享目录时，需要管理员手动设置

发布共享目录的格式:    
共享目录    [客户端1(参数1,参数2,…)] [客户端2(参数1,参数2,…)]…    
共享目录:指NFS服务器上需要给客户端共享出来的目录,在设置目录时需要使用绝对路径    
客户端  :是指所有可以访问共享目录的计算机    
{{ img("./img/6.png", "客户端", "图片挂了", "NFS") }}

参数    :是指客户端对共享目录的访问权限设置
{{ img("./img/7.png", "参数", "图片挂了", "NFS") }}

示例:
{{ img("./img/8.jpg", "示例", "图片挂了", "NFS") }}

在NFS服务器上，共享如下目录：
 - /media目录，允许所有客户端访问，但只具有只读权限
 - /NFS/public目录，允许192.168.1.0/24和196.168.2.0/24网段的客户端访问，且只具有只读权限
 - /NFS/team1目录，允许来自.team1.apple域的客户端访问，具有读写权限
 - /NFS/works目录，允许192.168.1.0/24网段客户端访问，并将root用户映射为匿名用户
 - /NFS/test目录，所有客户端允许访问，所有用户映射为匿名用户，并指定匿名用户的UID和GID均为65534
 - /NFS/security目录，仅允许192.168.1.254客户端访问，具有读写权限

2. 配置NFS固定端口
针对场景:NFS服务每次启动,其对应的端口号都会随机变化,这对服务器防火墙配置带来负担.因此,可以通过配置,固定NFS服务所用端口.    
配置文件{{ text("/etc/sysconfig/nfs", "success") }}增加如下配置行:    
MOUNT_PORT=”5001”    
STATD_PORT=“5002”    
LOCKD_UDPPORT=“5003”    
LOCKD_TCPPORT=“5003”    
RQUOTAD_PORT=“5004”

##NFS服务端测试
NFS服务启动/停止/重启/查询状态命令:
```shell
service portmap start/stop/restart/status
service nfs start/stop/restart/status
```
开机自动启动NFS服务命令:
```shell
chkconfig nfs on
```
停止开机自动启动NFS:
```shell
chkconfig nfs off
```

##NFS客户端配置
1. 查看NFS服务器的共享目录:
```shell
showmount –e 服务器名/IP
```
2. 挂载NFS文件系统:
```shell
mount –t nfs NFS服务器IP地址/主机名：共享目录  本地挂载点
```
例：将192.168.1.254上的/tmp目录挂载到本地的/test目录
```shell
mount –t nfs 192.168.1.254:/tmp /test
```
3. 卸载NFS文件系统:
```shell
umount 本地挂载点
```
4. 开机自动挂载NFS
配置客户端{{ text("/etc/fstab", "success") }}文件    
挂载目录格式：    
NFS服务器IP:共享目录  本地挂载点  nfs defaults 0 0    
{{ img("./img/9.jpg", "自动挂载NFS", "图片挂了", "NFS") }}

##其他
可能有人会这么问:如果我需要配置一个大型机群系统,这样每个节点都需要配置,那我岂不是需要一台一
台计算机去操作?这看起来好蠢啊!    
不是看起来很蠢,这本来就太蠢了...所以,我们需要一个更高效的方法,找更多的人帮你配!!好吧开个玩笑,
我要说的是有个系统可以帮助我们,那就是大名鼎鼎的Network Information Service,小名叫NIS.但如果不
想出事的话,你最好只是在内网使用,因为它的安全性真的不是很好.
