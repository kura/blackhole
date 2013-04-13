.PHONY: install uninstall travis coverage
install:
	python setup.py install

uninstall:
	pip uninstall blackhole

travis: install
	-easy_install nose coverage

coverage:
	nosetests --with-coverage blackhole
	coverage xml -i 