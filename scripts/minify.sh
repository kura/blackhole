#!/usr/bin/env sh
pip install htmlmin cssmin jsmin

find .tox/docs/tmp/html -type f -iname "*.html" |
  while read -r f
  do
    mv "$f" "$f.bak"
    htmlmin -cs "$f.bak" "$f"
    rm "$f.bak"
  done

find .tox/docs/tmp/html -type f -iname "*.css" |
  while read -r f
  do
    mv "$f" "$f.bak"
    cssmin < "$f.bak" > "$f"
    rm "$f.bak"
  done

find .tox/docs/tmp/html -type f -iname "*.js" |
  while read -r f
  do
    mv "$f" "$f.bak"
    python -m jsmin "$f.bak" > "$f"
    rm "$f.bak"
  done
