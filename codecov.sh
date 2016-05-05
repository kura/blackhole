#!/bin/bash

if test -f .codecov
then
  source .codecov
  codecov -t $CODECOV_TOKEN
fi
