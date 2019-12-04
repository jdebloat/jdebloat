.PHONY: setup
setup: jreduce-install inliner-build jshrink-build output

.PHONY: clean
clean: inliner-clean
	rm -rf ./output

.PHONY: jreduce-install
jreduce-install:
	cd tools/jreduce; stack install

output:
	mkdir output

.PHONY: inliner-build
inliner-build: output
	cp data/inliner/settings.py tools/jinline/src/python/settings.py
	cd tools/jinline; make setup
	cd tools/jinline; make

.PHONY: inliner-clean
inliner-clean:
	@-rm tools/jinline/build/inliner.jar
	@-rm ./output/db.sqlite3

.PHONY: experiments
experiments: output
	./Shakefile.hs output/all.csv

.PHONY: small-experiments
small-experiments: output
	./Shakefile.hs output/report.csv

.PHONY: jshrink-build
jshrink-build:
	cd tools/jshrink/experiment_resources/jshrink-mtrace/jmtrace; make JDK=/usr/lib/jvm/java-8-openjdk-amd64 OSNAME=linux
	cd tools/jshrink/jshrink; mvn compile -pl jshrink-app -am
	cd tools/jshrink; cp jshrink/jshrink-app/target/jshrink-app-1.0-SNAPSHOT-jar-with-dependencies.jar experiment_resources/
	cp scripts/run_jshrink.sh tools/jshrink/experiment_resources/run_experiment_script_all_transformations_with_tamiflex_and_jmtrace.sh
	chmod +x tools/jshrink/experiment_resources/run_experiment_script_all_transformations_with_tamiflex_and_jmtrace.sh
