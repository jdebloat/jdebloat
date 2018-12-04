#!/usr/bin/env python3

import sys
import json
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
        classpath.extend(filter(lambda x:x, line.strip().split(":")))
    return classpath

def extract_jar(jar, tofolder):
    tofolder.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(jar) as zfile:
        only = []
        for f in zfile.namelist():
            current = tofolder / Path(f)
            if current.is_file():
                shutil.rmtree(str(current), ignore_errors=True)
            if not f.startswith("META-INF"):
                only.append(f)
        zfile.extractall(path=str(tofolder), members=only)

def copy_classes(src, dst):
    for file in src.rglob("*"):
        if not file.is_file(): continue
        dst_file = dst / file.relative_to(src)
        dst_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.rmtree(str(dst_file), ignore_errors=True)
        shutil.copyfile(str(file), str(dst_file))

def make_jar(src, libs, jar, stage_folder=None):
    if not stage_folder: 
        stage_folder = jar.parent.parent / jar.stem
    for lib in libs:
        extract_jar(lib, stage_folder)
    copy_classes(src, stage_folder)
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
    excludedtest, benchmark, output = [Path(a) for a in argv[1:]]
  
    excluded = set(excludedtest.read_text().splitlines())

    extract = output / "extracted" / benchmark.name

    shutil.rmtree(str(extract), ignore_errors=True)
    extract.mkdir(parents=True, exist_ok=True)

    dct = extract_gitinfo(benchmark)
    
    target = benchmark / "target" 

    if not target.exists():
        build(benchmark)

    test_classes = set(extract_testclasses(target)) - excluded
    (extract / "test.classes.txt").write_text('\n'.join(test_classes) + '\n')
    
    compile_cp = set(extract_classpath(benchmark, "compile"))
    make_jar(target / "classes", compile_cp, extract / "jars" / "app+lib.jar") 
    
    test_cp = set(extract_classpath(benchmark, "test"))
    make_jar(target / "test-classes", test_cp - compile_cp, extract / "jars" / "test.jar")
    

    dct["classpath"] = {
        "app+lib": sorted(compile_cp),
        "test": sorted(test_cp - compile_cp)
        }

    dct["test"] = sorted(test_classes)

    with open(str(extract / "extract.json"), "w") as w: 
        json.dump(dct, w)


if __name__ == "__main__":
    main(sys.argv)
