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

packagedeployprod:
	python3 -m twine upload --repository pypi dist/* --verbose

packageall:
	make packagebuild
	make packagedeploytest
	make packagedeployprod