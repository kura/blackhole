#!/usr/bin/env sh

if test -f .codecov
then
  . .codecov
  codecov -t $CODECOV_TOKEN
fi
