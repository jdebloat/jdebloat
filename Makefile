benchmarks = $(shell sed -n 's/^\([^\#,]*\),.*/\1/p' data/benchmarks.csv | sed 1d)
downloads = $(patsubst %, output/benchmarks/%/TIMESTAMP, $(benchmarks))
extractions = $(patsubst %, output/extracted/%/extract.json, $(benchmarks))
testoutputs = $(patsubst %, output/tests/%.txt, $(benchmarks))
jreduce-outs = $(patsubst %, output/jreduce/%/app+lib.jar, $(benchmarks))
jshrink-outs = $(patsubst %, output/jshrink/%/TIMESTAMP, $(benchmarks))
inliner-outs = $(patsubst %, output/inliner/%/app+lib.jar, $(benchmarks))
jreduce-inliner-outs = $(patsubst %, output/inliner+jreduce/%/app+lib.jar, $(benchmarks))

.PHONY: all setup
all: output/benchmarks.csv $(testoutputs)

setup: jreduce-install inliner-build inliner-setup

$(downloads): output/benchmarks/%/TIMESTAMP: data/benchmarks.csv
	-git clone $(shell sed -n "s/$*,\([^,]*\),.*/\1/p" data/benchmarks.csv) output/benchmarks/$*;
	-(cd output/benchmarks/$*; git checkout -b onr $(shell sed -n "s/^$*,[^,]*,\([^,]*\)$$/\1/p" data/benchmarks.csv); git apply ../data/patches/$*.patch);
	touch $@;

$(extractions): output/extracted/%/extract.json: output/benchmarks/%/TIMESTAMP
	./scripts/benchmark.py data/excluded-tests.txt output/benchmarks/$* output

$(testoutputs): output/tests/%.txt: output/extracted/%/extract.json ./scripts/run-test.sh
	mkdir -p output/tests
	./scripts/run-test.sh output/extracted/$* 2>&1 | tee $@
## STATS

output/benchmarks.csv: $(extractions)
	jq -rs '["id","url","rev"],(sort_by(.id) | .[] | [.id,.url,.rev])| @csv' $^ > $@

output/reductions.csv: $(extractions) $(jreduce-outs) $(inliner-outs) 
	./scripts/metric.py output/extracted \
		inliner:output/inliner/%/app+lib.jar \
		jreduce:output/jreduce/%/app+lib.jar \
		>$@

output/jreduce.csv: $(extractions) $(jreduce-outs) ./scripts/metric.py
	./scripts/metric.py output/extracted \
		jreduce:output/jreduce/%/app+lib.jar \
		>$@

## JREDUCE

.PHONY: jreduce jreduce-install
jreduce: $(jreduce-outs)

jreduce-install:
	cd tools/jvmhs; stack install 

$(jreduce-outs): output/jreduce/%/app+lib.jar: output/extracted/%/extract.json ./scripts/run-jreduce.sh ./scripts/run-test.sh
	mkdir -p output/jreduce
	./scripts/run-jreduce.sh \
           output/extracted/$*/jars/test.jar \
           output/extracted/$*/test.classes.txt \
	   output/extracted/$*/jars/app+lib.jar \
	   output/jreduce/$* -o output/jreduce/$*/output -v
	(cd output/jreduce/$*/output; jar cf ../app+lib.jar *)

$(jreduce-inliner-outs): output/inliner+jreduce/%/app+lib.jar: output/inliner/%/app+lib.jar output/extracted/%/extract.json ./scripts/runjreduce.sh ./scripts/runtest.sh
	mkdir -p output/inliner+jreduce
	./scripts/runjreduce.sh \
           output/extracted/$*/jars/test.jar \
           output/extracted/$*/test.classes.txt \
	   $< \
	   output/inliner+jreduce/$* -o output/inliner+jreduce/$*/output -v 
	(cd output/inliner+jreduce/$*/output; jar cf ../app+lib.jar *)

## Debloat

.PHONY: jshrink
jshrink: output/shrink

output/jshrink: $(jshrink-outs)

$(jshrink-outs): output/jshrink/%/TIMESTAMP: output/benchmarks/%/TIMESTAMP output/extracted/%/extract.json ./scripts/run_jshrink.sh
	mkdir -p output/jshrink/
	cp -r output/extracted/$* output/jshrink/$*
	./scripts/run_jshrink.sh \
	$(CURDIR)/output/jshrink/$*/jars/app.jar \
	$(CURDIR)/output/jshrink/$*/jars/lib.jar \
	$(CURDIR)/output/jshrink/$*/jars/test.jar \
	$(CURDIR)/output/jshrink/$*/maven

	touch $@

~/.tamiflex/poa.properties: ~/.tamiflex
	cp tools/jshrink/poa.properties ~/.tamiflex/poa.properties

~/.tamiflex:
	mkdir ~/.tamiflex

## Inliner

.PHONY: inliner
inliner: inliner-build inliner-setup

.PHONY: inliner-build
inliner-build:
	cd tools/inliner; make

.PHONY: inliner-setup
inliner-setup: output/inliner
	cp data/inliner/settings.py tools/inliner/src/python/settings.py
	cd tools/inliner; DJANGO_SETTINGS_MODULE=settings make setup

.PHONY: inliner-clean
inliner-clean:
	rm -rf output/inliner

output/inliner:
	mkdir -p $@

$(inliner-outs): output/inliner/%/app+lib.jar: output/extracted/%/jars/app+lib.jar ./scripts/run-inliner.py
	./scripts/run-inliner.py \
           output/extracted/$*/jars/test.jar \
           output/extracted/$*/test.classes.txt \
	   output/extracted/$*/jars/app+lib.jar \
	   output/inliner/$* -o $@

.PHONY: clean clean-all
clean:
	rm -rf output

clean-all: clean
	git submodule foreach git clean -fdx
