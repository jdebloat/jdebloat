
.PHONY: clean 

extractions = $(patsubst benchmarks/%, output/extracted/%, $(wildcard benchmarks/*))

all: $(extractions)

output/extracted/%: benchmarks/%
	./scripts/benchmark.py $< output

clean: 
	rm -rf output


