benchmarks = $(sort $(wildcard benchmarks/*))
extractions = $(patsubst benchmarks/%, output/extracted/%/extract.json, $(benchmarks))
testoutputs = $(patsubst benchmarks/%, output/tests/%.txt, $(benchmarks))
jreduce-outs = $(patsubst benchmarks/%, output/jreduce/%/output, $(benchmarks))
debloat-outs = $(patsubst benchmarks/%, output/debloat/%/TIMESTAMP, $(benchmarks))

.PHONY: all
all: output/benchmarks.csv $(testoutputs)

$(extractions): output/extracted/%/extract.json: benchmarks/%
	-(cd $<; git apply ../../data/$*.patch)
	./scripts/benchmark.py data/excluded-tests.txt $< output

$(testoutputs): output/tests/%.txt: output/extracted/%/extract.json ./scripts/runtest.sh
	mkdir -p output/tests
	./scripts/runtest.sh $</jars/test.jar $</test.classes.txt $</jars/app+lib.jar 2>&1 | tee $@

## STATS

output/benchmarks.csv: $(extractions)
	jq -rs '["id","url","rev"],(sort_by(.id) | .[] | [.id,.url,.rev])| @csv' $^ > $@

output/reductions.csv: $(jreduce-outs) $(extractions) 
	./scripts/metric.py output/extracted jreduce:output/jreduce/%/output >$@

## JREDUCE

.PHONY: jreduce
jreduce: $(jreduce-outs)


$(jreduce-outs): output/jreduce/%/output: output/extracted/%/extract.json ./scripts/runjreduce.sh ./scripts/runtest.sh
	mkdir -p output/jreduce
	./scripts/runjreduce.sh $</jars/test.jar $</test.classes.txt $</jars/app+lib.jar output/jreduce/$* -o $@ -v


## Debloat

.PHONY: debloat
debloat: output/debloat

output/debloat: $(debloat-outs)

$(debloat-outs): output/debloat/%/TIMESTAMP: benchmarks/% output/extracted/%/extract.json ./scripts/rundebloat.sh
	mkdir -p output/debloat/
	cp -r benchmarks/$* output/debloat/$*
	./scripts/rundebloat.sh output/debloat/$*
	touch $@

~/.tamiflex/poa.properties: ~/.tamiflex
	cp tools/debloat/poa.properties ~/.tamiflex/poa.properties

~/.tamiflex:
	mkdir ~/.tamiflex

.PHONY: clean
clean:
	rm -rf output
