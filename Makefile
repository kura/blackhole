.PHONY: install uninstall travis coverage
install:
	python setup.py install

uninstall:
	pip uninstall blackhole

travis: install install_test

install_test:
	easy_install nose coveralls

coverage:
	nosetests --with-coverage blackhole
	coverage xml -i 