
.PHONY: clean 

build/benchmarks.csv: build
	./scripts/benchmark.py benchmarks build/benchmarks.csv

build/: 
	mkdir build

clean: 
	rm -rf build


