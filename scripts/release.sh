#!/usr/bin/env sh
pip install wheel twine
python setup.py sdist bdist_wheel
twine upload dist/*.whl dist/*.tar.*
