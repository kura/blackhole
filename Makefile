.PHONY: install uninstall travis coverage install_test
install:
	python setup.py install

uninstall:
	pip uninstall blackhole

travis: install install_test

install_test:
	pip nose

coverage:
	nosetests --with-coverage blackhole
	coverage xml -i 