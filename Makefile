.PHONY: install uninstall travis install_coverage install_testrig coverage pypi docs test
install:
	python setup.py install

install_coverage:
	pip install coverage coveralls

uninstall:
	pip uninstall blackhole

install_testrig:
	pip install nose

test: install_testrig
	nosetests

coverage: install_coverage travis

travis:
	coverage run --source=blackhole runtests.py

pypi:
	python setup.py sdist upload

docs:
	sphinx-build docs/source/ docs/build/
