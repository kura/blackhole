#!/usr/bin/env sh
pip install htmlmin cssmin jsmin

for f in `find docs/build -type f -iname "*.html"`
do
  mv $f $f.bak
  htmlmin -cs $f.bak $f
  rm $f.bak
done

for f in `find docs/build -type f -iname "*.css"`
do
  mv $f $f.bak
  cat $f.bak | cssmin > $f
  rm $f.bak
done

for f in `find docs/build -type f -iname "*.js"`
do
  mv $f $f.bak
  python -m jsmin $f.bak > $f
  rm $f.bak
done
