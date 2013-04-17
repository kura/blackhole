.PHONY: install uninstall travis install_coverage install_testrig coverage pypi docs
install:
	python setup.py install

install_coverage:
	pip install coverage coveralls

uninstall:
	pip uninstall blackhole

install_testrig:
	pip install unittest2

travis:
	nosetests --with-coverage --cover-erase --cover-package=blackhole

coverage:
	coverage xml -i

pypi:
	python setup.py sdist upload

docs:
	sphinx-build docs/source/ docs/build/
