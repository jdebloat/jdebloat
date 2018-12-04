.PHONY: clean 

extractions = $(patsubst benchmarks/%, output/extracted/%/extract.json, $(wildcard benchmarks/*))
testoutputs = $(patsubst benchmarks/%, output/tests/%.txt, $(wildcard benchmarks/*))

all: output/benchmarks.csv $(testoutputs)

output/benchmarks.csv: $(extractions)
	jq -rs '["id","url","rev"],(sort_by(.id) | .[] | [.id,.url,.rev])| @csv' $^ > $@

output/tests/%.txt: output/extracted/% ./scripts/runtest.sh
	mkdir -p output/tests
	APPCP=$</jars/app+lib.jar TESTCP=$</jars/test.jar TEST_CLASSES=$</test.classes.txt ./scripts/runtest.sh 2>&1 | tee $@
     
output/extracted/%/extract.json: benchmarks/%
	./scripts/benchmark.py data/excluded-tests.txt $< output

clean: 
	rm -rf output


