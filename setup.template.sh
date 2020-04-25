#!/bin/sh
set -e

# 添加架构
ARCHITECTURE=$(dpkg --print-architecture && dpkg --print-foreign-architectures)
if ! echo "$ARCHITECTURE" | grep -qE 'amd64|i386'; then
    echo "必须amd64/i386机型才能移植deepin-wine"
    return 1
fi
sudo dpkg --add-architecture i386

# 添加GPG公钥
GPG_KEY_CONTENT="<GPG_KEY_CONTENT>"
echo "$GPG_KEY_CONTENT" | base64 -d | sudo tee /etc/apt/trusted.gpg.d/i-m.dev.gpg >/dev/null

# 添加软件源
REPO="https://deepin-wine.i-m.dev"
LIST_FILE="/etc/apt/sources.list.d/deepin-wine.i-m.dev.list"

has_package() {
  apt-cache madison "$@" | grep -qv $REPO
}

if has_package libjpeg62-turbo; then
  if has_package python-gobject; then
    distributor=debian-stable
  else
    distributor=debian-testing
  fi
else
  distributor=ubuntu-bionic
fi

echo "deb ${REPO}/ ${distributor}/" | sudo tee $LIST_FILE >/dev/null

# 刷新软件源
sudo apt-get update -q

printf "\033[32;1m%s\033[0m\n" "
大功告成，现在可以试试安装deepin-wine软件了，
安装/更新TIM：sudo apt-get install deepin.com.qq.office
安装/更新QQ：sudo apt-get install deepin.com.qq.im
安装/更新微信：sudo apt-get install deepin.com.wechat"

printf "\033[36;1m%s\033[0m\n" "
如果觉得有用，请到 https://github.com/zq1997/deepin-wine 点个star吧😛"
