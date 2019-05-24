.PHONY: setup
setup: jreduce-install inliner-build 

.PHONY: clean 
clean: inliner-clean 
	rm -rf ./output

.PHONY: jreduce-install
jreduce-install:
	cd tools/jvmhs; stack install 

.PHONY: inliner-build
inliner-build: inliner-clean
	cp data/inliner/settings.py tools/inliner/src/python/settings.py
	cd tools/inliner; make setup
	cd tools/inliner; make	
	cp tools/inliner/src/python/db.sqlite3 output/db.sqlite3		

.PHONY: inliner-clean
inliner-clean:
	@-rm ./output/db.sqlite3
	@-rm ./tools/inliner/src/python/db.sqlite3

.PHONY: experiments
experiments:
	./Shakefile.hs output/all.csv

.PHONY: small-experiments
small-experiments:
	./Shakefile.hs output/report.csv
