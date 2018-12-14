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


def get_metric(categories, classpath): 
    out = check_output(['javaq', '--format', 'json-metric', '--cp', str(classpath)], universal_newlines=True)
    final = { c: 0 for c in categories } 
    for line in out.splitlines():
        dct = json.loads(line)
        del dct["name"]
        del dct["sha256"]
        for key in dct:
            final[key] += dct[key]
        final['classes'] += 1
    return dict(**final)


RE_TESTRUN = re.compile(r"Tests run: ([0-9]+)") 
RE_FAILURES = re.compile(r"Failures: ([0-9]+)")
RE_SUCCESS = re.compile(r"OK \(([0-9]+) tests*\)")

def run_test(extracted, classpath):

    try: 
        cmd = [ 'bash', 
                str(Path(sys.argv[0]).parent / "runtest.sh"), 
                str(extracted / "jars" / "test.jar"),
                str(extracted / "test.classes.txt"),
                str(classpath),
                ]
        out = check_output(cmd,
            universal_newlines=True,
            stderr=STDOUT
            )
   
        res = RE_SUCCESS.search(out)
        if res:
            return int(res.group(1)) 

    except CalledProcessError as e:
        try: 
            tests = RE_TESTRUN.search(str(e.output))
            failures = RE_FAILURES.search(str(e.output))
            return int(tests.group(1)) - int(failures.group(1))
        except AttributeError:
            return 0


def parseArg(a):
    a, b = a.split(':')
    return (a,b)

def main(args): 
    dct = OrderedDict(parseArg(a) for a in args[2:])

    base = Path(args[1])
    
    categories = ["size", "methods", "classes", "fields", "instructions", "tests"]
    columns = list(itertools.product(categories, dct))
    headers = ["id", "name", "libs"] + categories + [cat + ":" + v  for (cat,v ) in columns ]

    writer = csv.DictWriter(sys.stdout, fieldnames = headers)
    writer.writeheader()

    for p in sorted(base.iterdir()):
        line = {}
        id = p.name
        line["id"] = id

        basecp = p / "jars" / "app+lib.jar"

        base = get_metric(categories, basecp)
        base["tests"] = run_test(p, basecp)

        with open(str(p / "extract.json")) as x: 
            data = json.load(x)
            base["name"] = data["url"].split("/")[-1]
            base["libs"] = len(data["classpath"]["app+lib"])

        line.update(**base)
        print(id, "base", base, file=sys.stderr)
        results = {}
        for (key, path) in dct.items():
            cp = path.replace("%", id)
            results[key] = dict(get_metric(categories[:-1], cp))
            results[key]["tests"] = run_test(p, cp)
            print(id, key, results[key], file=sys.stderr)

        for cat, v in columns: 
            header = cat + ":" + v
            line[header] = results[v][cat] / base[cat]

        writer.writerow(line)

if __name__ == "__main__":
    main(sys.argv)



