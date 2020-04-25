# deepin-wine

> deepin-wine环境与应用在Mint/Ubuntu/Debian上的移植仓库
>
> 使用deepin官方原版软件包
>
> 安装QQ只需要`apt-get install`这么简单

## 快速开始

1. 添加仓库

   运行如下一行命令即可

   ```sh
   wget -O- https://deepin-wine.i-m.dev/setup.sh | sh
   ```

2. 应用安装

   现在，你可以像对待普通的软件包一样，使用`apt-get`系列命令进行各个deepin-wine应用安装、更新、卸载和依赖清理了。

   比如安装TIM只需要运行下面的命令，

   ```sh
   sudo apt-get install deepin.com.qq.office
   ```

   常用应用的软件包名如下：

   |    应用    |          包名           |
   | :--------: | :---------------------: |
   |    TIM     |  deepin.com.qq.office   |
   |     QQ     |    deepin.com.qq.im     |
   |  QQ轻聊版  | deepin.com.qq.im.light  |
   |    微信    |    deepin.com.wechat    |
   |  百度网盘  |  deepin.com.baidu.pan   |
   | 迅雷极速版 | deepin.com.thunderspeed |
   |   WinRAR   |  deepin.cn.com.winrar   |

   当然还有一些其他的应用，不全部列出。

## 添加仓库过程详解

**不关心细节的同学不必了解这部分，完全不影响使用**

环境配置其实就是添加我自行构建的软件仓库为源，具体包括以下三步。

1. 添加i386架构

   因为deepin-wine相关的软件包都是i386的，而现在的系统基本是64位的，所以需要先添加i386架构支持。

   通过`dpkg --print-architecture`和`dpkg --print-foreign-architectures`命令查看系统原生和额外添加的架构支持，如果输出结果不含`i386`，则需要手动添加支持。

   ```sh
   sudo dpkg --add-architecture i386
   ```

2. 添加GPG公钥

   使用第三方软件仓库需要添加其公钥。

   下载[i-m.dev.gpg](https://deepin-wine.i-m.dev/i-m.dev.gpg)复制到`/etc/apt/trusted.gpg.d/`目录即可，或者直接运行

   ```sh
   sudo wget -O /etc/apt/trusted.gpg.d/i-m.dev.gpg "https://deepin-wine.i-m.dev/i-m.dev.gpg"
   ```

3. 添加软件源

   创建`/etc/apt/sources.list.d/deepin-wine.i-m.dev.list`文件，并先添加如下内容，

   ```
   deb https://deepin-wine.i-m.dev/deepin/ <发型版兼容类型>/
   ```

   其中，`<发型版兼容类型>`应当替换为以下值之一：

   - debian-stable
   - debian-testing
   - ubuntu-bionic
   - ubuntu-focal

   这需要根据Linux系统的实际发行版判断。

   例如，Linux Mint 19.3是基于Ubuntu 18.04（Bionic），所以应该填写`ubuntu-bionic`。

   也有可能，有些发行版不是基于上述版本，但是“歪打正着”兼容了上述版本，可以逐一尝试。

   如果都无法使用，可以在issue中提出。

4. 刷新软件源

   ```sh
   sudo apt-get update
   ```

## 卸载清理

卸载与清理按照层次从浅到深可以分为如下四个层级，

1. 清理应用运行时目录

   例如QQ/TIM会把帐号配置、聊天文件等保存`~/Documents/Tencent Files`目录下，而微信是`~/Documents/WeChat Files`，删除这些文件夹以移除帐号配置等数据。

2. 清理wine容器

   删除`~/.deepinwine/`目录下相应名称的文件夹即可。

3. 卸载软件包

   常规的`sudo apt-get purge xxx`和`sudo apt-get autoremove`操作。

4. 移除软件仓库

   ```sh
   sudo rm /etc/apt/trusted.gpg.d/i-m.dev.gpg /etc/apt/sources.list.d/deepin-wine.i-m.dev.list
   sudo apt-get update
   ```
   
   这会把一切恢复到最初初始的状态。

## 版权相关

这个git仓库中的代码只包括了移植版软件仓库的构建工具，最后仓库中软件包的下载地址会被301重定向到deepin的官方仓库（及镜像）中去，其版权由[deepin](https://www.deepin.com/)所有。

## 感谢

本工作是参考了**wszqkzqk**的[deepin-wine-ubuntu](https://github.com/wszqkzqk/deepin-wine-ubuntu)工作，在此基础上进行了高更一层的包装，让使用变得方便一点。同时，此项目的兼容wszqkzqk的项目，已经按照wszqkzqk项目安装好后，依然可以再按此项目进行配置，可以更方便地进行后续管理。
