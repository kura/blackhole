#!/bin/sh
wget https://api.github.com/repos/libuv/libuv/tarball -O libuv.tar.gz
mkdir libuv
tar xzvf libuv.tar.gz -C libuv --strip-components 1
pushd libuv
./autogen.sh
./configure
make
sudo make install
popd
rm -rf libuv*
