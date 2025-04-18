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
	python ./testcases/main.py