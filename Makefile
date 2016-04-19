.PHONY: clean install uninstall tox test lint docs release web
clean:
	find . -name "*.pyc" -delete

install:
	python setup.py install

uninstall:
	pip uninstall blackhole

tox:
	pip install tox detox
	detox

test:
	pip install pytest pytest-cov coveralls sphinx
	py.test --cov ./blackhole --cov ./tests --doctest-modules --verbose ./blackhole ./tests
	sphinx-build -b html docs/source/ docs/build/

lint:
	pip install flake8 pylint
	flake8 blackhole
	pylint blackhole

docs:
	pip install sphinx
	sphinx-build -b html docs/source/ docs/build/

release:
	pip install twine wheel
	python setup.py sdist bdist_wheel
	twine upload dist/*

web:
	make docs
	knock ego.kura.io && rsync -avhr -e "/usr/bin/ssh -p 2222" docs/build/ ego.kura.io:/var/www/blackhole.io/
