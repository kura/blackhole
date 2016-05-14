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

test:
	pip install pytest pytest-cov pytest-asyncio codecov sphinx
	py.test --cov ./blackhole \
	        --cov ./tests \
			--verbose \
			./blackhole ./tests \
			--cov-report xml \
			--cov-report term-missing
	bash codecov.sh
	sphinx-build -b html docs/source/ docs/build/

lint:
	pip install flake8 pylint
	flake8 blackhole
	pylint blackhole

docs:
	pip install sphinx
	rm -rf docs/build
	sphinx-build -b html docs/source/ docs/build/

release:
	bash release.sh

web:
	make docs
	knock ego.kura.io && rsync -avhr -e "/usr/bin/ssh -p 2222" docs/build/ ego.kura.io:/var/www/blackhole.io/
	rm -rf docs/build

testssl:
	sudo apt-get install -y aha
	testssl.sh --wide --colorblind blackhole.io:465 | aha | grep -v 'Start' | grep -v 'Done' | grep -v '/usr/bin/openssl' | sed 's/stdin/testssl.sh/g' | awk -v RS= -v ORS='\n\n' '1' > docs/source/_extra/testssl.sh.html
