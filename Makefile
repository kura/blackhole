.PHONY: autodocs clean docs install manpages pipenv release test pipenv testssl tox uninstall

clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
	rm -rf docs/build
	rm -rf man/build

docs: clean
	pip install sphinx guzzle_sphinx_theme cssmin jsmin htmlmin
	rm -rf docs/build
	sphinx-build -j 4 docs/source/ docs/build/
	./htmlmin.sh
	./cssmin.sh
	./jsmin.sh

install:
	python setup.py install

man: clean
	pip install docutils
	mkdir -p man/build
	rst2man.py man/source/blackhole.rst man/build/blackhole.1
	rst2man.py man/source/blackhole_config.rst man/build/blackhole_config.1

release:
	./release.sh

test: clean docs man pipenv
	pip install codecov \
				pycodestyle \
				pydocstyle \
				pyflakes \
				pylama \
				pytest \
				pytest-cov \
				pytest-asyncio \
				setproctitle \
				radon
	py.test --cov ./blackhole \
			--cov ./tests \
			--cov-report xml \
			--cov-report term-missing \
			--pylama \
			--verbose \
			--cache-clear \
			blackhole tests
	radon mi -nc blackhole
	./codecov.sh

pipenv:
	pip install pipenv
	pipenv check
	pipenv install

testssl:
	sudo apt-get install -y aha
	testssl.sh --wide --colorblind blackhole.io:465 | aha | grep -v 'Start' | grep -v 'Done' | grep -v '/usr/bin/openssl' | sed 's/stdin/testssl.sh/g' | awk -v RS= -v ORS='\n\n' '1' > docs/source/_extra/testssl.sh.html

tox:
	pip install tox detox
	detox

uninstall:
	pip uninstall blackhole
