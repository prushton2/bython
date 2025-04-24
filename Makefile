install:
	pyinstaller --onefile ./src/bython.py
	mv ./dist/bython /bin/bython
	pyinstaller --onefile ./src/py2by.py
	mv ./dist/py2by /bin/py2by
	make clean
clean:
	rm *.spec
	rm -rf dist
	rm -rf build
uninstall:
	rm /bin/bython
	rm /bin/by2py
test:
	python ./tests/main.py
packagebuild:
	rm -rf ./dist
	python3 -m build
packagedeploytest:
	python3 -m twine upload --repository testpypi dist/* --verbose