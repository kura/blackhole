.PHONY: install uninstall travis install_coverage coverage
install:
	python setup.py install

install_coverage:
	pip install coverage coveralls

uninstall:
	pip uninstall blackhole

travis:
	nosetests --with-coverage blackhole

coverage:
	coverage xml -i 