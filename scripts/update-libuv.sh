#!/bin/sh
git clone https://github.com/libuv/libuv.git
cd libuv || return
git checkout "$(git describe --tags)"
./autogen.sh
./configure
make
sudo make install
cd .. || return
rm -rf libuv*
