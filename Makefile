.PHONY: autodoc
autodoc:
	pip install sphinx guzzle_sphinx_theme sphinx-autobuild
	sphinx-autobuild -B docs/source docs/build

.PHONY: build
build:
	rm -rf build dist
	pip install wheel
	python setup.py sdist bdist_wheel

.PHONY: clean
clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
	rm -rf build dist docs/build man/build t coverage.xml .coverage .coverage.* .testmondata .testmondata-journal

.PHONY: docs
docs: clean linkcheck
	pip install sphinx guzzle_sphinx_theme
	sphinx-build -j 4 docs/source/ docs/build/
	scripts/minify.sh

.PHONY: install
install:
	python setup.py install

.PHONY: install_tox
install_tox:
	pip install tox

.PHONY: lint
lint: install_tox
	tox -e lint

.PHONY: man
man: clean
	pip install docutils
	mkdir -p man/build
	rst2man.py man/source/blackhole.rst man/build/blackhole.1
	rst2man.py man/source/blackhole_config.rst man/build/blackhole_config.1

.PHONY: pre-commit
pre-commit:
	tox -e pre-commit

.PHONY: release
release: clean install_tox
	tox -e build
	twine upload dist/*.whl dist/*.tar.*

.PHONY: shellcheck
shellcheck: install_tox
	tox -e shellcheck

.PHONY: test
test: install_tox
	tox -e py36

.PHONY: test_py36
test_py36: install_tox
	tox -e py36,py36-setproctitle,py36-uvloop,py36-uvloopandsetproctitle

.PHONY: test_py37
test_py37: install_tox
	tox -e py37,py37-setproctitle,py37-uvloop,py37-uvloopandsetproctitle

.PHONY: test_build
test_build: install_tox
	tox -e build

.PHONY: test_docs
test_docs: install_tox
	tox -e docs

.PHONY: test_man
test_man: install_tox
	tox -e man

.PHONY: test_pipfile
test_pipfile: install_tox
	tox -e pipfile

.PHONY: test_setuppy
test_setuppy: install_tox
	tox -e setuppy

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

.PHONY: update-libuv
update-libuv:
	scripts/update-libuv.sh

.PHONY: watch
watch:
	tox -e watch
