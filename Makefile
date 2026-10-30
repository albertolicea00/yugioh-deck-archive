.PHONY: run install db-en db-es convert validate clean lint

PYTHON ?= python
PIP ?= pip

run:
	$(PYTHON) main.py

install:
	$(PIP) install -r requirements.txt

db-en:
	mkdir -p data
	curl -L -o data/cards.cdb \
		"https://raw.githubusercontent.com/ryoken08/CDBEsp/master/cards.cdb"

convert:
	$(PYTHON) scripts/deck-convert.py

validate:
	$(PYTHON) scripts/deck-validate.py

lint:
	$(PYTHON) -m py_compile main.py
	$(PYTHON) -m py_compile theme/__init__.py
	find core screens widgets -name '*.py' -exec $(PYTHON) -m py_compile {} +

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -name '*.pyc' -delete
	rm -rf build dist *.spec .kivy
