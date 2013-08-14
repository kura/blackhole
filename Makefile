.PHONY: install uninstall install_coverage install_testrig install_tox tox test coverage travis pypi docs web tag release
install:
	python setup.py install

uninstall:
	pip uninstall blackhole

install_coverage:
	pip install coverage coveralls

install_testrig:
	pip install nose

install_tox:
	pip install tox detox

tox: install_tox
	detox

test: install_testrig
	nosetests

coverage: install_coverage travis

travis:
	coverage run --source=blackhole runtests.py

pypi:
	python setup.py sdist bdist_egg bdist_wheel upload

docs:
	pip install sphinx
	sphinx-build docs/source/ docs/build/

web: docs
	rsync -e "ssh -p 2222" -P -rvz --delete docs/build/ kura@blackhole.io:/var/www/blackhole.io/

tag:
	sed -i 's/__version__ = ".*"/__version__ = "${version}"/g' blackhole/__init__.py
	git add blackhole/__init__.py
	git ci -m "New release ${version}"
	git push origin master
	git tag ${version}
	git push --tags

release:
	tag ${version}
	pypi
	web
