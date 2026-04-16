ifeq ($(OS),Windows_NT)
    PYTHON := python
    VENV_PYTHON := venv/Scripts/python.exe
    VENV_PIP := venv/Scripts/pip.exe
    RM := rmdir /s /q
else
    PYTHON := python3
    VENV_PYTHON := venv/bin/python
    VENV_PIP := venv/bin/pip
    RM := rm -rf
endif

help:
	@echo "make setup   — tworzy srodowisko i instaluje zaleznosci"
	@echo "make run     — uruchamia eksperyment"
	@echo "make analyse — uruchamia analize danych"
	@echo "make plot    — uruchamia wykresy"
	@echo "make freeze  — zapisuje zaleznosci do requirements.txt"
	@echo "make clean   — usuwa srodowisko wirtualne"

setup:
	$(PYTHON) -m venv venv
	$(VENV_PIP) install --upgrade pip
	$(VENV_PIP) install -r requirements.txt

run: $(VENV_PYTHON)
	@if [ -n "$$VIRTUAL_ENV" ]; then \
		python uwaga.py; \
	else \
		$(VENV_PYTHON) uwaga.py; \
	fi

analyze: $(VENV_PYTHON)
	@if [ -n "$$VIRTUAL_ENV" ]; then \
		python analyzer.py; \
	else \
		$(VENV_PYTHON) analyzer.py; \
	fi

plot: $(VENV_PYTHON)
	@if [ -n "$$VIRTUAL_ENV" ]; then \
		python plotter.py; \
	else \
		$(VENV_PYTHON) plotter.py; \
	fi

freeze:
	$(VENV_PIP) freeze > requirements.txt

clean:
	$(RM) venv
