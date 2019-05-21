.PHONY: setup
setup: jreduce-install inliner-build 
	./Shakefile.hs setup

.PHONY: clean
clean: 
	./Shakefile.hs clean
	./Shakefile.hs setup

.PHONY: jreduce-install
jreduce-install:
	cd tools/jvmhs; stack install 

.PHONY: inliner-build
inliner-build:
	cp data/inliner/settings.py tools/inliner/src/python/settings.py
	cd tools/inliner; DJANGO_SETTINGS_MODULE=settings make setup
	cd tools/inliner; make

.PHONY: experiments
experiments:
	./Shakefile.hs output/all.csv

.PHONY: small-experiments
small-experiments:
	./Shakefile.hs output/report.csv
