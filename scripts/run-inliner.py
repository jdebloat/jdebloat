#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys
import shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def update_modified_files_in_place(original_dir, modified_dir):
    for root, dirs, files in os.walk(original_dir):
        for name in files:
            original_path = os.path.join(root, name)
            path = os.path.relpath(original_path, original_dir)
            modified_path = os.path.join(modified_dir, path)
            if os.path.exists(modified_path):
                shutil.copyfile(modified_path, original_path)

def main(args):
    test_jar = os.path.join(BASE_DIR, args.test_jar)
    app_lib_jar = os.path.join(BASE_DIR, args.app_lib_jar)
    test_classes = os.path.join(BASE_DIR, args.test_classes)

    tool_dir = os.path.join(BASE_DIR, 'tools', 'inliner')
    build_dir = os.path.join(tool_dir, 'build')
    script_path = os.path.join(tool_dir, 'scripts', 'create-inline-targets.sh') 

    output_dir = os.path.join(BASE_DIR, args.output_dir)
    inline_targets_path = os.path.join(output_dir, 'inline-targets.txt')
    output_files_path = os.path.join(output_dir, 'files')
    output_soot_path = os.path.join(output_dir, 'sootOutput')
    output_jar = os.path.join(BASE_DIR, args.output_jar)
    
    classpath = '{}:{}'.format(test_jar, app_lib_jar)

    test_runner = None
    TEST_RUNNER_CHOICES = ['org.junit.runner.JUnitCore',
                           'junit.textui.TestRunner']
    for test_runner_choice in TEST_RUNNER_CHOICES:
        p = subprocess.run(['javap', '-cp', classpath, test_runner_choice],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if p.returncode == 0:
            test_runner = test_runner_choice
            break
    assert test_runner is not None

    test_args = []
    with open(test_classes, 'r') as f:
        test_args.append(test_runner)
        for line in f:
            test_args.append(line.strip())

    print('\033[1;34mInliner: {}\033[m'.format(output_dir))
    os.makedirs(output_dir, exist_ok=True)

    skip_log = False
    for path in os.listdir(output_dir):
        if path.endswith('.log'):
            skip_log = True

    if not skip_log:
        print('\033[36mRunning original tests...\033[m')
        subprocess.run(['java',
                        "-XX:+UnlockDiagnosticVMOptions", "-XX:+LogCompilation",
                        "-Xcomp",
                        "-XX:MinInliningThreshold=1",
                        "-XX:MaxInlineSize=70",
                        '-cp', classpath] + test_args, cwd=output_dir)
    else:
        print('\033[33mSkipped running original tests and generating inline targets...\033[m')

    if not skip_log:
        for path in os.listdir(output_dir):
            if path.endswith('.log'):
                print('\033[36mGenerating inline targets...\033[m')
                subprocess.run([script_path, output_dir,
                                os.path.join(output_dir, path), inline_targets_path],
                               env=dict(os.environ, DJANGO_SETTINGS_MODULE='settings'))

    print('\033[36mExtracting original JAR files...\033[m')
    subprocess.run(['unzip', '-q', '-o', app_lib_jar, '-d', output_files_path])

    print('\033[36mTransforming class files...\033[m')
    subprocess.run(['java', '-Xmx2g',
                    '-cp', "{}:{}".format(os.path.join(build_dir, 'soot.jar'),
                                          os.path.join(build_dir, 'inliner.jar')),
                    'InlinerTool.Main',
                    '-process-dir', output_files_path,
                    '-d', output_soot_path,
                    inline_targets_path])

    if not os.path.exists(output_soot_path):
        shutil.rmtree(output_files_path)
        subprocess.run(['cp', app_lib_jar, output_jar])
        print('\033[31mNo Soot output, exiting...\033[m')
        exit(0)

    print('\033[36mOverwriting modified files...\033[m')
    update_modified_files_in_place(output_files_path, output_soot_path)

    if os.path.exists(output_jar):
        print('\033[33mRemoving previously modified JAR...\033[m')
        os.remove(output_jar)

    print('\033[36mCreating modified JAR...\033[m')
    subprocess.run(['jar', 'cf', output_jar, '-C', output_files_path, '.'])

    print('\033[36mCleaning up temporary files...\033[m')
    shutil.rmtree(output_files_path)
    shutil.rmtree(output_soot_path)

    print('\033[36mRe-running tests...\033[m')
    modified_classpath = '{}:{}'.format(test_jar, output_jar)
    subprocess.run(['java', '-cp', modified_classpath] + test_args)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run inliner tool.')
    parser.add_argument('test_jar', help='JAR containing the test suite')
    parser.add_argument('test_classes', help='Text file of test classes')
    parser.add_argument('app_lib_jar', help='JAR containing application and libraries')
    parser.add_argument('output_dir', help='Output directory')
    parser.add_argument('-o', dest='output_jar', help='Modified JAR file path')
    args = parser.parse_args()
    main(args)
