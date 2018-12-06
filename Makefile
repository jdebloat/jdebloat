extractions = $(patsubst benchmarks/%, output/extracted/%/extract.json, $(wildcard benchmarks/*))
testoutputs = $(patsubst benchmarks/%, output/tests/%.txt, $(wildcard benchmarks/*))

.PHONY: all
all: output/benchmarks.csv $(testoutputs)

$(extractions): output/extracted/%/extract.json: benchmarks/%
	./scripts/benchmark.py data/excluded-tests.txt $< output

$(testoutputs): output/tests/%.txt: output/extracted/% ./scripts/runtest.sh
	mkdir -p output/tests
	APPCP=$</jars/app+lib.jar TESTCP=$</jars/test.jar TEST_CLASSES=$</test.classes.txt ./scripts/runtest.sh 2>&1 | tee $@

output/benchmarks.csv: $(extractions)
	jq -rs '["id","url","rev"],(sort_by(.id) | .[] | [.id,.url,.rev])| @csv' $^ > $@

.PHONY: clean
clean:
	rm -rf output
