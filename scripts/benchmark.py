#!/usr/bin/env python3

import sys
import json
import tempfile
import re
import shutil
import csv
import os
import zipfile
from subprocess import check_output, run, CalledProcessError
from pathlib import Path
from contextlib import contextmanager

# https://stackoverflow.com/questions/431684/how-do-i-change-directory-cd-in-python
@contextmanager
def changedir(dir):
    prevdir = os.getcwd()
    try:
        os.chdir(os.path.expanduser(str(dir)))
        yield
    finally:
        os.chdir(prevdir)

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

def extract_gitinfo(benchmark):
    with changedir(benchmark):
        url = git("remote", "get-url", "origin")[0]
        rev = git("rev-list", "-n", 1, "HEAD")[0]
        return { "id": benchmark.name, "url": url, "rev": rev }

def build(benchmark):
    with changedir(benchmark):
        run([ "mvn",
            "-Dmaven.repo.local=libs",
            "install",
            "--batch-mode",
            "-fn"])

def extract_classpath(benchmark, scope):
    with changedir(benchmark):
        lines = read("mvn", "dependency:build-classpath",
                "-Dmaven.repo.local=libs",
                "-DincludeScope={}".format(scope),
                "--batch-mode")

        classpath = []
        for line in lines:
            if line.startswith("[INFO]"): continue
            for x in line.strip().split(":"):
                if not x: continue
                l = [str(Path.cwd()), x]
                prefix = os.path.commonprefix(l)
                if str(prefix) != str(Path.cwd()): continue
                classpath.append(x)
    return classpath

def extract_jar(jar, tofolder):
    Path(tofolder).mkdir(parents=True, exist_ok=True)
    run(["unzip", "-qo", str(jar), "-d", str(tofolder)])

def copy_files(src, dst):
    for file in src.rglob("*"):
        if not file.is_file(): continue
        dst_file = dst / file.relative_to(src)
        dst_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.rmtree(str(dst_file), ignore_errors=True)
        shutil.copyfile(str(file), str(dst_file))

def make_jar(srcs, libs, jar):
    with tempfile.TemporaryDirectory() as stage_folder: 
        for lib in libs:
            extract_jar(lib, stage_folder)
        for src in srcs:
            copy_files(src, stage_folder)
        jar.parent.mkdir(parents=True, exist_ok=True)
        absjar = jar.parent.resolve() / jar.name
        with changedir(stage_folder):
            run(["jar", "cf", str(absjar), "."])

def extract_testclasses(target):
    expr = re.compile(r'.*/surefire-reports/TEST-(.*)\.xml$')
    test_classes = []
    for x in (target / "surefire-reports").rglob("*.xml"):
        test_classes.append(expr.match(str(x)).group(1))
    return test_classes

def main(argv):
    excludedtest, benchmark, extract = [Path(a) for a in argv[1:]]

    excluded = set(excludedtest.read_text().splitlines())

    shutil.rmtree(str(extract), ignore_errors=True)
    extract.mkdir(parents=True, exist_ok=True)

    dct = extract_gitinfo(benchmark)


    print("Looking at: " + str(benchmark))
    if not (benchmark / "libs").exists():
        print("Building")
        build(benchmark)
    
    targets = list(benchmark.glob("*/target/classes"))
    test_targets = list(benchmark.glob("*/target/test-classes"))
    resources = list(benchmark.glob("*/src/test/resources"))
    if (benchmark / "target").exists(): 
        targets.append(benchmark / "target" / "classes")
        test_targets.append(benchmark / "target" / "test-classes")

    test_classes = set.union(*[set(extract_testclasses(t.parent)) for t in test_targets]) - excluded
    (extract / "test.classes.txt").write_text('\n'.join(test_classes) + '\n')

    make_jar(targets, set(), extract / "app.jar")
    
    compile_cp = set(extract_classpath(benchmark, "compile"))
    make_jar([], compile_cp, extract / "lib.jar")

    test_cp = set(extract_classpath(benchmark, "test"))
    make_jar(test_targets, test_cp - compile_cp, extract / "test.jar")

    for t in resources:
        x = t.parent.parent
        copy_files(t, extract / "src" / t.relative_to(x))

    dct["classpath"] = {
        "lib": sorted(compile_cp),
        "test": sorted(test_cp - compile_cp)
        }

    dct["test"] = sorted(test_classes)

    with open(str(extract / "extract.json"), "w") as w:
        json.dump(dct, w)


if __name__ == "__main__":
    
    main(sys.argv)
