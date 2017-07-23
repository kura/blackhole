#!/usr/bin/env sh
for f in `find docs/build -type f -iname "*.css"`
do
  mv $f $f.bak
  cat $f.bak | cssmin > $f
  rm $f.bak
done
