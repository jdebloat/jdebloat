extractions = $(patsubst benchmarks/%, output/extracted/%/extract.json, $(wildcard benchmarks/*))
testoutputs = $(patsubst benchmarks/%, output/tests/%.txt, $(wildcard benchmarks/*))

jreduce-outs = $(patsubst benchmarks/%, output/jreduce/%, $(wildcard benchmarks/*))

.PHONY: all
all: output/benchmarks.csv $(testoutputs)

$(extractions): output/extracted/%/extract.json: benchmarks/%
	-(cd $<; git apply ../../data/$*.patch)
	./scripts/benchmark.py data/excluded-tests.txt $< output

$(testoutputs): output/tests/%.txt: output/extracted/% ./scripts/runtest.sh
	mkdir -p output/tests
	./scripts/runtest.sh $</jars/test.jar $</test.classes.txt $</jars/app+lib.jar 2>&1 | tee $@

## STATS

output/benchmarks.csv: $(extractions)
	jq -rs '["id","url","rev"],(sort_by(.id) | .[] | [.id,.url,.rev])| @csv' $^ > $@


## JREDUCE

.PHONY: jreduce
jreduce: $(jreduce-outs)

$(jreduce-outs): output/jreduce/%: output/extracted/% ./scripts/runjreduce.sh ./scripts/runtest.sh
	mkdir -p output/jreduce
	./scripts/runjreduce.sh $</jars/test.jar $</test.classes.txt $</jars/app+lib.jar $@ -o $@/output 


.PHONY: clean
clean:
	rm -rf output
