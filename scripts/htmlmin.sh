#!/usr/bin/env sh
for f in `find docs/build -type f -iname "*.html"`
do
  mv $f $f.bak
  htmlmin -cs $f.bak $f
  rm $f.bak
done
