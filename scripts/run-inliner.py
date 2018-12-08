#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys
import shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main(args):
    extracted_dir = os.path.join(BASE_DIR, 'output', 'extracted',
                                 args.benchmark)
    output_dir = os.path.join(BASE_DIR, 'output', 'inliner', args.benchmark)
    tool_dir = os.path.join(BASE_DIR, 'tools', 'inliner')
    build_dir = os.path.join(tool_dir, 'build')
    script_path = os.path.join(tool_dir, 'scripts', 'create-inline-targets.sh') 
    inline_targets_path = os.path.join(output_dir, 'inline-targets.txt')
    soot_output_path = os.path.join(output_dir, 'sootOutput')
    extracted_jar_path = os.path.join(extracted_dir, "app+lib")
    new_jar_classfiles_path = os.path.join(soot_output_path, 'app+lib')
    new_app_lib_jar_path = os.path.join(BASE_DIR, output_dir, "app+lib.jar")
    test_jar = os.path.join(extracted_dir, 'jars', 'test.jar')
    app_lib_jar = os.path.join(extracted_dir, 'jars', 'app+lib.jar')
    
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
    with open(os.path.join(extracted_dir, 'test.classes.txt'), 'r') as f:
        test_args.append(test_runner)
        for line in f:
            test_args.append(line.strip())

    os.makedirs(output_dir, exist_ok=True)

    print('\033[1;34mInliner: {}\033[m'.format(output_dir))

    skip_log = False
    for path in os.listdir(output_dir):
        if path.endswith('.log'):
            skip_log = True
    cmd = ['java', "-XX:+UnlockDiagnosticVMOptions", "-XX:+LogCompilation",
           "-Xcomp", "-XX:MinInliningThreshold=1", "-XX:MaxInlineSize=70", 
           '-cp', classpath] + test_args

    if not skip_log:
        print('\033[36mRunning original tests...\033[m')
        subprocess.run(cmd, cwd=output_dir)
    else:
        print('\033[33mSkipped running original tests and generating inline targets...\033[m')

    if not skip_log:
        for path in os.listdir(output_dir):
            if path.endswith('.log'):
                print('\033[36mGenerating inline targets...\033[m')
                subprocess.run([script_path, args.benchmark,
                               os.path.join(output_dir, path), inline_targets_path])

    print('\033[36mTransforming class files...\033[m')
    soot_tool_cmd = ['java', '-Xmx2g',
                     '-cp', "{}:{}".format(os.path.join(build_dir, 'soot.jar'),
                                           os.path.join(build_dir, 'inliner.jar')),
                     'InlinerTool.MainDriver', '-process-dir',
                     extracted_jar_path,
                     '-d', soot_output_path, inline_targets_path]
    print('[DEBUG]', ' '.join(soot_tool_cmd))
    subprocess.run(soot_tool_cmd)

    print("Create new jar")
    print("copy old classfiles")
    cp_original_classfiles_cmd = ['cp', '-r', extracted_jar_path, soot_output_path]
    print('\033[36m[REMOVE] Running:\033[m {}'.format(' '.join(cp_original_classfiles_cmd)))
    subprocess.run(cp_original_classfiles_cmd)
 
    print("copy new classfiles") 
    new_classfile_dirs = []
    for filename in os.listdir(soot_output_path):
        if filename != 'app+lib':
            new_classfile_dirs.append(os.path.join(soot_output_path,filename))
    cp_new_classfiles_cmd = ['cp', '-r'] + new_classfile_dirs + [new_jar_classfiles_path]
    print('\033[36m[REMOVE] Running:\033[m {}'.format(' '.join(cp_new_classfiles_cmd)))
    subprocess.run(cp_new_classfiles_cmd)

    print("run jar command")
    create_jar_cmd = ['jar', 'cf', new_app_lib_jar_path, '-C', new_jar_classfiles_path, '.']
    print('\033[36m[REMOVE] Running:\033[m {}'.format(' '.join(create_jar_cmd)))
    subprocess.run(create_jar_cmd)


    print("Re-check tests")
    classpath = '{}:{}'.format(test_jar, new_app_lib_jar_path)
    recheck_cmd = ['java', '-cp', classpath] + test_args
    print('\033[36m[REMOVE] Running:\033[m {}'.format(' '.join(recheck_cmd)))
    subprocess.run(recheck_cmd)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run inliner tool.')
    parser.add_argument('benchmark', help='benchmark to run, e.g. 01')
    args = parser.parse_args()
    main(args)
