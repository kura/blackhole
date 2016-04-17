.PHONY: clean install uninstall tox test lint docs release
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
	pip install pytest pytest-cov coveralls
	py.test --cov ./blackhole --cov ./tests --doctest-modules --verbose ./blackhole ./tests

lint:
	pip install flake8 pylint
	pylint blackhole

docs:
	pip install sphinx
	sphinx-build -b html docs/source/ docs/build/

release:
	pip install twine wheel
	python setup.py sdist bdist_wheel
	twine upload dist/*
