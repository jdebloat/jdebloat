#!/usr/bin/env python3

import sys
import csv
from subprocess import check_output
from pathlib import Path

def read(cmd, *args, **kwargs):
    return check_output([cmd] + list(args), universal_newlines=True).split('\n')

def git(*cmd, work_folder="."):
    args = []
    args += ['-C', str(work_folder)]
    args += [str(c) for c in cmd]
    return read("git", *args)

def handle_benchmark(benchmark):
    url = git("remote", "get-url", "origin", work_folder=benchmark)[0]
    rev = git("rev-list", "-n", 1, "HEAD", work_folder=benchmark)[0]
    return { "id": benchmark.name, "url": url, "rev": rev }

def main(argv):
    with open(argv[2], "w") as w: 
        writer = csv.DictWriter(w, ["id", "url", "rev"])
        writer.writeheader()
        for benchmark in sorted(Path(argv[1]).iterdir()):
            dct = handle_benchmark(benchmark)
            writer.writerow(dct)

if __name__ == "__main__":
    main(sys.argv)
