#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main(args):
    extracted_dir = os.path.join(BASE_DIR, 'output', 'extracted',
                                 args.benchmark)
    test_jar = os.path.join(extracted_dir, 'jars', 'test.jar')
    app_lib_jar = os.path.join(extracted_dir, 'jars', 'app+lib.jar')
    classpath = '{}:{}'.format(test_jar, app_lib_jar)

    test_runner = None
    TEST_RUNNER_CHOICES = ['org.junit.runner.JUnitCore',
                           'junit.textui.TestRunner']
    for test_runner_choice in TEST_RUNNER_CHOICES:
        p = subprocess.run(['java', '-cp', classpath, 'org.junit.runner.JUnitCore'],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if p.returncode == 0:
            test_runner = test_runner_choice
            break
    assert test_runner is not None

    test_classes = []
    with open(os.path.join(extracted_dir, 'test.classes.txt'), 'r') as f:
        for line in f:
            test_classes.append(line.strip())

    cmd = ['java', '-cp', classpath, test_runner] + test_classes
    subprocess.run(cmd)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run inliner tool.')
    parser.add_argument('benchmark', help='benchmark to run, e.g. 01')
    args = parser.parse_args()
    main(args)
