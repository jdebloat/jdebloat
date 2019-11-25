import csv
import os
from pathlib import Path
from subprocess import check_output, run, CalledProcessError
import sys
import tempfile

BENCHMARKS = "data/benchmarks.csv"
ROOT = Path(os.path.dirname(os.path.abspath(__file__)))
OUTPUT= ROOT / "output"
DATA= ROOT / "data"
PATCHES = DATA / "patches"
SRC_FOLDER = "benchmark"
SCRIPTS = ROOT / "scripts"
TARGETS = ["initial", "initial+jshrink"]
ALL_TARGETS = [
    "initial",
    "initial+jshrink"
]

def main():
    if(os.path.exists(str(OUTPUT / "all.csv"))):
        return

    benchmarks = get_benchmarks()

    for benchmark in benchmarks:
        download_benchmark(benchmark)
        apply_patch(benchmark)
        for target in TARGETS:
            run_target(benchmark, target)

    write_stats(benchmarks)

def write_stats(benchmarks):
    stats = []
    for benchmark in benchmarks:
        for target in TARGETS:
            with open(str(OUTPUT / benchmark.id / target / "stats.csv")) as f:
                stats.append(f.readlines()[-1])

    with open(str(OUTPUT / "all.csv"), "w") as f:
        f.write("id,name,size,methods,classes,fields,instructions,tests\n")
        f.writelines(stats)

def run_target(benchmark, target):
    target = target.split("+")
    source = OUTPUT / benchmark.id / SRC_FOLDER

    for i in range(0, len(target)):
        t = target[i]
        dest = OUTPUT / benchmark.id / "+".join(target[0:i + 1])

        if t == "initial":
            compile(benchmark, source, dest)
        elif t == "inliner":
            inline(source, dest)
        elif t == "jreduce":
            jreduce(source, dest)
        elif t == "jshrink":
            jshrink(source, dest)

        test(dest)
        metric(dest)

        source = dest
        #run tests

def read(*args, **kwargs):
    try:
        return check_output(args, universal_newlines=True, **kwargs).splitlines()
    except CalledProcessError as e:
        print('Failed, while running: ', ' '.join('{!r}'.format(c) for c in args), file=sys.stderr)
        raise

def git(*cmd, work_folder="."):
    args = []
    args += ['-C', str(work_folder)]
    args += [str(c) for c in cmd]
    return read("git", *args)

def compile(benchmark, src, dest):
    if(os.path.exists(str(dest / "app.jar"))):
      return

    run([str(SCRIPTS / "benchmark.py"), str(DATA / "excluded-tests.txt"), str(src), str(dest)])

def jreduce(src, dest):
    if(os.path.exists(str(dest / "app.jar"))):
        return
    output = read(str(SCRIPTS / "run-jreduce.sh"), str(src), str(dest))

    with open(str(dest / "test.txt"), "w") as f:
      f.write(str(output))

def inline(src, dest):
    if(os.path.exists(str(dest / "app.jar"))):
        return

    run([str(SCRIPTS / "run-inliner.sh"), str(src), str(dest)])

def jshrink(src, dest):
    if(os.path.exists(str(dest / "app.jar"))):
        return

    run([str(SCRIPTS / "jshrink_script.sh"), str(src), str(dest)])

def test(dest):
    if(os.path.exists(str(dest / "test.txt"))):
        return

    with tempfile.TemporaryDirectory() as dirpath:
        os.chdir(dirpath)
        run([str(SCRIPTS / "run-test.sh"), str(dest)])
        os.chdir(str(ROOT))

def metric(dest):
    if(os.path.exists(str(dest / "stats.csv"))):
        return

    output = read(str(SCRIPTS / "metric.py"), str(dest))
    with open(str(dest / "stats.csv"), "w") as f:
      f.write(str(output))

def apply_patch(benchmark):
    path = OUTPUT / benchmark.id / SRC_FOLDER / "TIMESTAMP"
    patch_path = str(PATCHES / benchmark.id) + ".patch"

    if(os.path.exists(str(path))):
        return

    if(os.path.exists(str(patch_path))):
        git("apply", patch_path, work_folder=path)

    with open(str(path), 'w'): pass

def download_benchmark(benchmark):
    path = OUTPUT / benchmark.id / SRC_FOLDER
    if(os.path.exists(str(path / ".git" / "HEAD"))):
        return

    if(os.path.exists(str(path))):
        os.rmdir(path)

    git("clone", benchmark.url, path)
    git("checkout", "-b", "onr", benchmark.rev, work_folder=path)

def get_benchmarks():
    data = []
    with open(BENCHMARKS) as bench_file:
        reader = csv.reader(bench_file, delimiter=',')
        next(reader) #skip header
        for row in reader:
            data.append(Benchmark(row[0], row[1], row[2]))
    return data

class Benchmark:
    def __init__(self, id, url, rev):
        self.id = id
        self.url = url
        self.rev = rev

if __name__ == "__main__":
    main()
