.PHONY: autodoc
autodoc:
	pip install sphinx guzzle_sphinx_theme sphinx-autobuild
	sphinx-autobuild -B docs/source docs/build

.PHONY: build
build:
	pip install wheel
	python setup.py sdist bdist_wheel

.PHONY: clean
clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
	rm -rf docs/build man/build .tox build dist

.PHONY: docs
docs: clean linkcheck
	pip install sphinx guzzle_sphinx_theme
	sphinx-build -j 4 docs/source/ docs/build/
	scripts/minify.sh

.PHONY: install
install:
	python setup.py install

.PHONY: linkcheck
linkcheck: clean
	pip install sphinx guzzle_sphinx_theme
	sphinx-build -j 4 -b linkcheck docs/source/ docs/build

.PHONY: man
man: clean
	pip install docutils
	mkdir -p man/build
	rst2man.py man/source/blackhole.rst man/build/blackhole.1
	rst2man.py man/source/blackhole_config.rst man/build/blackhole_config.1

.PHONY: pipfile
pipfile:
	pip install pipenv
	pipenv check
	pipenv install

.PHONY: release
release:
	scripts/release.sh

.PHONY: test
test: clean
	pip install codecov \
				pycodestyle \
				pydocstyle \
				pyflakes \
				pylama \
				pytest \
				pytest-asyncio \
				pytest-cov \
				radon \
				setproctitle
	py.test --cov ./blackhole \
			--cov ./tests \
			--cov-report xml \
			--cov-report term-missing \
			--verbose \
			--pylama \
			--cache-clear \
			blackhole tests
	radon mi -nc blackhole

.PHONY: testall
testall: tox

.PHONY: testssl
testssl:
	sudo apt-get install -y aha
	testssl.sh --wide --colorblind blackhole.io:465 | aha | grep -v 'Start' | grep -v 'Done' | grep -v '/usr/bin/openssl' | sed 's/stdin/testssl.sh/g' | awk -v RS= -v ORS='\n\n' '1' > docs/source/_extra/testssl.sh.html

.PHONY: tox
tox:
	pip install tox detox
	detox

.PHONY: uninstall
uninstall:
	pip uninstall blackhole
