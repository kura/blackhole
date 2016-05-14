#!/bin/bash

last_rel=`blackhole -v`
echo "Current version: ${last_rel}"

read -p "New version: " version

sed -i "s/__version__.*/__version = '${version}'/g" blackhole/__init__.py
git add blackhole/__init__.py
git ci -m "${version}"
git push origin master
git tag $version
git push --tags
make release
make web
