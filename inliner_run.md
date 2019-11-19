```
make setup (jreduce-install inliner-build mkdiroutput)
git clone https://github.com/aragozin/jvm-tools output/01/benchmark
cd output/01/benchmark
git checkout -b onr 65ab61f56694426247ab62bb27e13c17de8c5953
cd ../../..
./scripts/benchmark.py data/excluded-tests.txt output/01/benchmark output/01/initial
mkdir output/01/initial+inliner
./scripts/run-inliner.sh output/01/initial output/01/initial+inliner
```

