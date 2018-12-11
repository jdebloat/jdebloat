SHELL := /bin/bash

.PHONY: all
all: build build/inliner.jar soot

.PHONY: soot
soot:
	cd external/soot; mvn clean compile assembly:single
	cp external/soot/target/sootclasses-trunk-jar-with-dependencies.jar build/soot.jar

build:
	mkdir build

build/inliner.jar: src/java/InlinerTool/InlinerTransformer.java src/java/InlinerTool/Main.java
	javac -cp build/soot.jar $^ -d build
	jar cf $@ -C build 'InlinerTool'
	rm -rf build/InlinerTool

.PHONY: setup
setup:
	cd src/python; python3 -m venv venv; source venv/bin/activate; pip install -r requirements.txt; python manage.py migrate
