install:
	make clean
	pyinstaller --onefile ./src/bython-prushton2/bython.py
	mv ./dist/bython /bin/bython
	pyinstaller --onefile ./src/bython-prushton2/py2by.py
	mv ./dist/py2by /bin/py2by
	make clean

uninstall:
	rm /bin/bython
	rm /bin/by2py

clean:
	-rm *.spec
	-rm -rf ./dist
	-rm -rf ./build

test:
	cd ./src; \
	python ../tests/main.py

prodtest:
	cd ./venv; \
	python ../tests/main.py

packagebuild:
	make clean
	python3 -m build

packagedeploytest:
	python3 -m twine upload --repository testpypi dist/* --verbose

packagedeploy:
	python3 -m twine upload --repository pypi dist/* --verbose

packageall:
	make packagebuild
	make packagedeploytest
	make packagedeploy