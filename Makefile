
.PHONY: clean 

output/benchmarks.csv: 
	./scripts/benchmark.py benchmarks output

clean: 
	rm -rf output


