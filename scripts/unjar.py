#!/usr/bin/env python3

import sys
import os
import tempfile
from pathlib import Path 
from subprocess import check_output, run, CalledProcessError, DEVNULL
from contextlib import contextmanager
from collections import defaultdict
from itertools import zip_longest

# https://stackoverflow.com/questions/431684/how-do-i-change-directory-cd-in-python
@contextmanager
def changedir(dir):
    prevdir = os.getcwd()
    try:
        os.chdir(os.path.expanduser(str(dir)))
        yield
    finally:
        os.chdir(prevdir)

def extract_jar(jar, tofolder, files=[]):
    run(["unzip", "-nqqq", str(jar), "-d", str(tofolder)] + [f for f in files if f], stderr=DEVNULL)

def make_jar(absjar, fromfolder):
    with changedir(fromfolder):
        run(["jar", "cf", str(absjar), "."])

def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)

def main():
    """Given a list of jars print a list of files join the files in one jar
 
    These two commands are adjoint.

    $ unjar.py join app+lib.jar app.jar lib.jar > files.txt
    
    $ unjar.py split app+lib.jar < files.text
    
    """
    _, cmd, target, *args = sys.argv 

    if cmd == "join":
        with tempfile.TemporaryDirectory() as stage_folder: 
            files = set() 
            for jar in args:
                extract_jar(jar, stage_folder)
                added = set(a.relative_to(stage_folder) for a in Path(stage_folder).rglob("**/*")) - files
                for a in added:
                    print(jar, a)
                files |= added
            make_jar(os.path.realpath(target), stage_folder)
    elif cmd == "split":
        dist = defaultdict(set)
        for line in sys.stdin.readlines():
            jarname, filename  = line.split()
            dist[jarname].add(filename)
        for n in args:
            with tempfile.TemporaryDirectory() as stage_folder: 
                for x in grouper(sorted(dist[n]), 10, ""):
                    extract_jar(target, stage_folder, files=x) 
                make_jar(os.path.realpath(n), stage_folder)
    else:
        sys.stderr.write("Expected 'join' or 'split' as initial command.\n")



if __name__ == "__main__":
    main()
