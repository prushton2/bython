install:
	pyinstaller --onefile ./src/bython
	mv ./dist/bython /bin/bython
	pyinstaller --onefile ./src/py2by
	mv ./dist/py2by /bin/py2by
	make clean
clean:
	rm *.spec
	rm -rf dist
	rm -rf build
uninstall:
	rm /bin/bython
	rm /bin/by2py
