SHELL	:= /bin/bash
PYTHON	= /usr/bin/python

bdist:
	$(PYTHON) setup.py bdist
	
sdist:
	$(PYTHON) setup.py sdist

clean:
	/bin/rm -rf build dist
