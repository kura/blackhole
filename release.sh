#!/usr/bin/env sh

last_rel=`blackhole -v`
echo "Current version: ${last_rel}"

printf "New version: "
read version

sed -i "s/__version__.*/__version__ = '${version}'/g" blackhole/__init__.py
git add blackhole/__init__.py
git ci -m "${version}"
git push origin master
git tag $version
git push --tags
pip install wheel
python setup.py sdist bdist_wheel upload
rm -rf dist/build
make web
