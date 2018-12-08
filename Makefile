extractions = $(patsubst benchmarks/%, output/extracted/%/extract.json, $(wildcard benchmarks/*))
testoutputs = $(patsubst benchmarks/%, output/tests/%.txt, $(wildcard benchmarks/*))

jreduce-outs = $(patsubst benchmarks/%, output/jreduce/%, $(wildcard benchmarks/*))

.PHONY: all
all: output/benchmarks.csv $(testoutputs)

.PHONY: jreduce
jreduce: $(jreduce-outs)

.PHONY: debloat
debloat: output/debloat

$(extractions): output/extracted/%/extract.json: benchmarks/%
	./scripts/benchmark.py data/excluded-tests.txt $< output

$(testoutputs): output/tests/%.txt: output/extracted/% ./scripts/runtest.sh
	mkdir -p output/tests
	./scripts/runtest.sh $</jars/test.jar $</test.classes.txt $</jars/app+lib.jar 2>&1 | tee $@

$(jreduce-outs): output/jreduce/%: output/extracted/% ./scripts/runjreduce.sh ./scripts/runtest.sh
	mkdir -p output/jreduce
	./scripts/runjreduce.sh $</jars/test.jar $</test.classes.txt $</jars/app+lib.jar $@

output/benchmarks.csv: $(extractions)
	jq -rs '["id","url","rev"],(sort_by(.id) | .[] | [.id,.url,.rev])| @csv' $^ > $@

output/debloat: ~/.tamiflex/poa.properties
	mkdir -p output/debloat
	cp -r benchmarks output/debloat/benchmarks
	./scripts/rundebloat.sh output/debloat/benchmarks

~/.tamiflex/poa.properties: ~/.tamiflex
	cp tools/debloat/poa.properties ~/.tamiflex/poa.properties

~/.tamiflex:
	mkdir ~/.tamiflex

.PHONY: clean
clean:
	rm -rf output
