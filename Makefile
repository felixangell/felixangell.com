.PHONY: all serve dev

all:
	python3 scripts/build.py

serve: all
	python3 -m http.server 8000 --bind 127.0.0.1

dev:
	python3 -B scripts/dev.py
