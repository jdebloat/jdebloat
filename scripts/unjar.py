#!/usr/bin/env python3

import sys
import os
import tempfile
from pathlib import Path 
from subprocess import check_output, run, CalledProcessError
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


def extract_jar(jar, tofolder):
    run(["unzip", "-nq", str(jar), "-d", str(tofolder)])

def make_jar(absjar, fromfolder):
    with changedir(fromfolder):
        run(["jar", "cf", str(absjar), "."])

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
                added = set(a.relative_to(stage_folder) for a in Path(stage_folder).rglob("**")) - files
                for a in added:
                    print(jar, a)
                files |= added
            make_jar(os.path.realpath(target), stage_folder)
    elif cmd == "split":
        pass
    else:
        sys.stderr.write("Expected 'join' or 'split' as initial command.\n")



if __name__ == "__main__":
    main()
