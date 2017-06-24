#!/usr/bin/env sh
for f in `find docs/build -type f -iname "*.js"`
do
  mv $f $f.bak
  python -m jsmin $f.bak > $f
  rm $f.bak
done
