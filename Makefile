benchmarks = $(sort $(wildcard benchmarks/*))
extractions = $(patsubst benchmarks/%, output/extracted/%/extract.json, $(benchmarks))
testoutputs = $(patsubst benchmarks/%, output/tests/%.txt, $(benchmarks))
jreduce-outs = $(patsubst benchmarks/%, output/jreduce/%/output, $(benchmarks))
jdebloat-outs = $(patsubst benchmarks/%, output/jdebloat/%/TIMESTAMP, $(benchmarks))
inliner-outs = $(patsubst benchmarks/%, output/inliner/%/app+lib.jar, $(benchmarks))
jreduce-inliner-outs = $(patsubst benchmarks/%, output/inliner+jreduce/%/output, $(benchmarks))

.PHONY: all
all: output/benchmarks.csv $(testoutputs)

$(extractions): output/extracted/%/extract.json: benchmarks/%
	-(cd $<; git apply ../../data/$*.patch)
	./scripts/benchmark.py data/excluded-tests.txt $< output

$(testoutputs): output/tests/%.txt: output/extracted/%/extract.json ./scripts/runtest.sh
	mkdir -p output/tests
	./scripts/runtest.sh \
           output/extracted/$*/jars/test.jar \
           output/extracted/$*/test.classes.txt \
	   output/extracted/$*/jars/app+lib.jar 2>&1 | tee $@
## STATS

output/benchmarks.csv: $(extractions)
	jq -rs '["id","url","rev"],(sort_by(.id) | .[] | [.id,.url,.rev])| @csv' $^ > $@

output/reductions.csv: $(extractions) $(jreduce-outs) $(inliner-outs) $(jreduce-inliner-outs)
	./scripts/metric.py output/extracted \
		inliner:output/inliner/%/app+lib.jar \
		jreduce:output/jreduce/%/output \
		inliner+jreduce:output/inliner+jreduce/%/output \
		>$@

## JREDUCE

.PHONY: jreduce
jreduce: $(jreduce-outs)

$(jreduce-outs): output/jreduce/%/output: output/extracted/%/extract.json ./scripts/runjreduce.sh ./scripts/runtest.sh
	mkdir -p output/jreduce
	./scripts/runjreduce.sh \
           output/extracted/$*/jars/test.jar \
           output/extracted/$*/test.classes.txt \
	   output/extracted/$*/jars/app+lib.jar \
	   output/jreduce/$* -o $@ -v \

$(jreduce-inliner-outs): output/inliner+jreduce/%/output: output/inliner/%/app+lib.jar output/extracted/%/extract.json ./scripts/runjreduce.sh ./scripts/runtest.sh
	mkdir -p output/inliner+jreduce
	./scripts/runjreduce.sh \
           output/extracted/$*/jars/test.jar \
           output/extracted/$*/test.classes.txt \
	   $< \
	   output/inliner+jreduce/$* -o $@ -v \

## Debloat

.PHONY: jdebloat
jdebloat: output/jdebloat

output/jdebloat: $(jdebloat-outs)

$(jdebloat-outs): output/jdebloat/%/TIMESTAMP: benchmarks/% output/extracted/%/extract.json ./scripts/runjdebloat.sh
	mkdir -p output/jdebloat/
	cp -r benchmarks/$* output/jdebloat/$*
	./scripts/runjdebloat.sh output/jdebloat/$*
	touch $@

~/.tamiflex/poa.properties: ~/.tamiflex
	cp tools/jdebloat/poa.properties ~/.tamiflex/poa.properties

~/.tamiflex:
	mkdir ~/.tamiflex

## Inliner

.PHONY: inliner
inliner: inliner-build inliner-setup $(inliner-outs)

.PHONY: inliner-build
inliner-build:
	cd tools/inliner; make

.PHONY: inliner-setup
inliner-setup: output/inliner
	cp data/inliner/settings.py tools/inliner/src/python/settings.py
	cd tools/inliner; DJANGO_SETTINGS_MODULE=settings make setup

output/inliner:
	mkdir -p $@

$(inliner-outs): output/inliner/%/app+lib.jar: benchmarks/% output/extracted/%/extract.json ./scripts/run-inliner.py
	./scripts/run-inliner.py \
           output/extracted/$*/jars/test.jar \
           output/extracted/$*/test.classes.txt \
	   output/extracted/$*/jars/app+lib.jar \
	   output/inliner/$* -o $@

.PHONY: clean
clean:
	rm -rf output
