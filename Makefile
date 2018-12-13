benchmarks = $(sort $(wildcard benchmarks/*))
extractions = $(patsubst benchmarks/%, output/extracted/%/extract.json, $(benchmarks))
testoutputs = $(patsubst benchmarks/%, output/tests/%.txt, $(benchmarks))
jreduce-outs = $(patsubst benchmarks/%, output/jreduce/%/output, $(benchmarks))
jdebloat-outs = $(patsubst benchmarks/%, output/jdebloat/%/TIMESTAMP, $(benchmarks))

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

.PHONY: clean
clean:
	rm -rf output
