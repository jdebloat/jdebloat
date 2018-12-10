#!/usr/bin/env python3
"""
Caluclate a line in a csv file from the name and classpath of the tools.

./scripts/metric.py jreduce:output/jreduce/%/output

"""

import sys
import re
import json
import csv
import itertools
from pathlib import Path 
from subprocess import check_output, DEVNULL, STDOUT, CalledProcessError
from collections import OrderedDict, defaultdict


def get_metric(classpath): 
    out = check_output(['javaq', '--format', 'json-metric', '--cp', str(classpath)], universal_newlines=True)
    final = defaultdict(lambda: 0)
    for line in out.splitlines():
        dct = json.loads(line)
        del dct["name"]
        del dct["sha256"]
        for key in dct:
            final[key] += dct[key]
        final['classes'] += 1
    return dict(**final)


RE_FAILURE = re.compile(r"Test run: ([0-9]+), Failures: ([0-9]+)")
RE_SUCCESS = re.compile(r"OK \(([0-9]+) tests\)")

def run_test(extracted, classpath):

    try: 
        cmd = [ 'bash', 
                str(Path(sys.argv[0]).parent / "runtest.sh"), 
                str(extracted / "jars" / "test.jar"),
                str(extracted / "test.classes.txt"),
                str(classpath),
                ]
        print(cmd)
        out = check_output(cmd,
            universal_newlines=True,
            stderr=STDOUT
            )
   
        print(out)
        res = RE_SUCCESS.search(out)
        if res:
            return int(res.group(1)) 

    except CalledProcessError as e:
        print(e.output)
        res = RE_FAILURE.search(e.output)
        if res:
            return int(res.group(1)) - int(res.group(2))


def parseArg(a):
    a, b = a.split(':')
    return (a,b)

def main(args): 
    dct = OrderedDict(parseArg(a) for a in args[1:])

    base = Path("output/extracted/")
    
    categories = ["size", "methods", "classes", "fields", "instructions", "tests"]
    columns = list(itertools.product(categories, dct))
    headers = ["id"] + categories + [cat + ":" + v  for (cat,v ) in columns ]

    writer = csv.DictWriter(sys.stdout, fieldnames = headers)
    writer.writeheader()

    for p in sorted(base.iterdir()):
        line = {}
        id = p.name
        line["id"] = id

        basecp = p / "jars" / "app+lib.jar"
        base = get_metric(basecp)
    
        base["tests"] = run_test(p, basecp)

        line.update(**base)
        print(id, "base", base, file=sys.stderr)
        results = {}
        for (key, path) in dct.items():
            cp = path.replace("%", id)
            results[key] = dict(get_metric(cp))
            results[key]["tests"] = run_test(p, cp)
            print(id, key, results[key], file=sys.stderr)

        for cat, v in columns: 
            header = cat + ":" + v
            line[header] = results[v][cat] / base[cat]

        writer.writerow(line)

if __name__ == "__main__":
    main(sys.argv)



