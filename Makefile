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
	pip install twine wheel
	python setup.py sdist bdist_wheel
	twine upload dist/*

docs:
	pip install sphinx
	sphinx-build -b html docs/source/ docs/build/

web: docs
	rsync -e "ssh -p 2222" -P -rvz --delete docs/build/ kura@blackhole.io:/var/www/blackhole.io/

tag:
	bumpversion minor
	git push origin master
	git push --tags

release:
	tag
	pypi
	web
