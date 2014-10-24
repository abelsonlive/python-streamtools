
clean:
	rm -rf build/ dist/ *egg-info/ .DS_Store

build:
	python setup.py install 

publish:
	python setup.py sdist bdist_wininst upload

test:
	nosetests

