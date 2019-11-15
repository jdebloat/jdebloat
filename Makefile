.PHONY: setup
setup: jreduce-install inliner-build output

.PHONY: clean
clean: inliner-clean
	rm -rf ./output

.PHONY: jreduce-install
jreduce-install:
	cd tools/jvmhs; stack install

output:
	mkdir output

.PHONY: inliner-build
inliner-build: output
	cp data/inliner/settings.py tools/jinline/src/python/settings.py
	cd tools/jinline; make setup
	cd tools/jinline; make
	cp tools/jinline/src/python/db.sqlite3 output/db.sqlite3

.PHONY: inliner-clean
inliner-clean:
	@-rm tools/jinline/build/inliner.jar
	@-rm ./output/db.sqlite3
	@-rm ./tools/jinline/src/python/db.sqlite3

.PHONY: experiments
experiments: output
	./Shakefile.hs output/all.csv

.PHONY: small-experiments
small-experiments: output
	./Shakefile.hs output/report.csv
