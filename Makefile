.PHONY: clean install uninstall install_testrig tox test coverage travis flake8 pypi docs web tag release
clean:
	find . -name "*.pyc" -delete

install:
	python setup.py install

uninstall:
	pip uninstall blackhole

install_testrig:
	pip install nose mock

tox:
	pip install tox detox
	detox

test: install_testrig
	nosetests

coverage:
	pip install coverage
	travis

travis:
	pip install coveralls
	coverage run --source=blackhole runtests.py

flake8:
	pip install flake8
	flake8 blackhole --ignore="F403"

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
