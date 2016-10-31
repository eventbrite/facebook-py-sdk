build:
	python setup.py sdist
	python setup.py bdist_wheel --python-tag py2
	BUILD_VERSION=3 python3 setup.py bdist_wheel --python-tag py3

publish:
	python setup.py sdist upload
	python setup.py bdist_wheel --python-tag py2 upload
	BUILD_VERSION=3 python3 setup.py bdist_wheel --python-tag py3 upload

clean:
	find . -name '*.py[co]' -delete
	rm -rf python_social_auth.egg-info dist build

.PHONY:publish