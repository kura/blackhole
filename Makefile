.PHONY: clean install uninstall tox test autodocs docs manpages release testssl
clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete

install:
	python setup.py install

uninstall:
	pip uninstall blackhole

tox:
	pip install tox detox
	detox

test: docs manpages
	pip install pytest \
				pytest-cov \
				pytest-asyncio \
				pylama \
				pyflakes \
				pycodestyle \
				pydocstyle==1.1.1 \
				isort \
				codecov
	py.test --cov ./blackhole \
			--cov ./tests \
			--cov-report xml \
			--cov-report term-missing \
			--pylama \
			--verbose \
			--cache-clear \
			blackhole tests
	./codecov.sh

autodocs: docs
	pip install sphinx-autobuild
	sphinx-autobuild -z blackhole docs/source docs/build

docs:
	pip install sphinx guzzle_sphinx_theme
	rm -rf docs/build
	sphinx-build -j 4 docs/source/ docs/build/

manpages:
	pip install docutils
	rm -rf man/build
	mkdir -p man/build
	rst2man.py man/source/blackhole.rst man/build/blackhole.1
	rst2man.py man/source/blackhole_config.rst man/build/blackhole_config.1

release:
	./release.sh

testssl:
	sudo apt-get install -y aha
	testssl.sh --wide --colorblind blackhole.io:465 | aha | grep -v 'Start' | grep -v 'Done' | grep -v '/usr/bin/openssl' | sed 's/stdin/testssl.sh/g' | awk -v RS= -v ORS='\n\n' '1' > docs/source/_extra/testssl.sh.html
