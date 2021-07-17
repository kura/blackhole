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

.PHONY: lint
lint:
	tox -e lint

.PHONY: man
man: clean test_man
	mkdir -p man/build
	mv .tox/man/tmp/*.1 man/build

.PHONY: pre-commit
pre-commit:
	tox -e pre-commit

.PHONY: publish
publish:
	tox -e publish

.PHONY: release
release: publish

.PHONY: shellcheck
shellcheck:
	tox -e shellcheck

.PHONY: test
test:
	tox -vv -e py38

.PHONY: test_py37
test_py37:
	tox -vvp -e py37,py37-setproctitle,py37-uvloop

.PHONY: test_py38
test_py38:
	tox -vvp -e py38,py38-setproctitle,py38-uvloop

.PHONY: test_py39
test_py39:
	tox -vvp -e py39,py39-setproctitle,py39-uvloop

.PHONY: test_pypy3
test_pypy:
	tox -vvp -e pypy3,pypy3-setproctitle,py39-uvloop

.PHONY: test_pyston-3
test_pyston-3:
	tox -vvp -e pyston-3,pyston-3-setproctitle,pyston-3-uvloop

.PHONY: test_build
test_build:
	tox -e build

.PHONY: test_docs
test_docs:
	tox -e docs

.PHONY: test_man
test_man:
	tox -e man

.PHONY: test_poetry
test_poetry:
	tox -e poetry

.PHONY: test_setuppy
test_setuppy:
	tox -e setuppy

.PHONY: testall
testall: tox

.PHONY: testssl
testssl:
	sudo apt-get install -y aha
	testssl.sh --wide --colorblind blackhole.io:465 | aha | grep -v 'Start' | grep -v 'Done' | grep -v '/usr/bin/openssl' | sed 's/stdin/testssl.sh/g' | awk -v RS= -v ORS='\n\n' '1' > docs/source/_extra/testssl.sh.html

.PHONY: tox
tox:
	tox -e `tox -l | grep -v watch | tr '\n' ','` -p all

.PHONY: uninstall
uninstall:
	pip uninstall blackhole

.PHONY: update-libuv
update-libuv:
	scripts/update-libuv.sh

.PHONY: watch
watch:
	tox -e watch
