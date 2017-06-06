.PHONY: clean install uninstall tox test lint docs release web testssl
clean:
	find . -name "*.pyc" -delete

install:
	python setup.py install

uninstall:
	pip uninstall blackhole

tox:
	pip install tox detox
	detox

test: docs
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

docs:
	rm -rf docs/build
	sphinx-build -b html docs/source/ docs/build/

release:
	./release.sh

testssl:
	sudo apt-get install -y aha
	testssl.sh --wide --colorblind blackhole.io:465 | aha | grep -v 'Start' | grep -v 'Done' | grep -v '/usr/bin/openssl' | sed 's/stdin/testssl.sh/g' | awk -v RS= -v ORS='\n\n' '1' > docs/source/_extra/testssl.sh.html
