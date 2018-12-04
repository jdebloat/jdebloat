#!/usr/bin/env python3

import sys
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
        return check_output(args, universal_newlines=True, **kwargs).split('\n')
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
        zfile.extractall(
                path=str(tofolder), 
                members=[f for f in zfile.namelist() if f.endswith(".class")])

def copy_classes(src, dst):
    for file in src.rglob("*.class"):
        dst_file = dst / file.relative_to(src)
        dst_file.parent.mkdir(parents=True, exist_ok=True)
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
    benchmark, output = [Path(a) for a in argv[1:]]
    
    extract = output / "extracted" / benchmark.name
    extract.mkdir(parents=True, exist_ok=True)

    benchmarkscsv = output / "benchmarks.csv"
    with open(str(benchmarkscsv), "a") as w: 
        writer = csv.DictWriter(w, ["id", "url", "rev"])

        dct = extract_gitinfo(benchmark)
        writer.writerow(dct)

        build(benchmark)
        
        target = benchmark / "target" 

        compile_cp = set(extract_classpath(benchmark, "compile"))
        make_jar(target / "classes", compile_cp, extract / "jars" / "app+lib.jar") 
        
        test_cp = set(extract_classpath(benchmark, "test"))
        make_jar(target / "test-classes", test_cp - compile_cp, extract / "jars" / "test.jar")
        
        test_classes = extract_testclasses(target)
        (extract / "test.classes.txt").write_text('\n'.join(test_classes))

if __name__ == "__main__":
    main(sys.argv)
