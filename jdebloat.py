#!/usr/bin/python3
import csv
import os
from pathlib import Path
import subprocess
from subprocess import check_output, run, CalledProcessError
import sys
import tempfile
from contextlib import contextmanager
import shutil
from argparse import ArgumentParser, RawTextHelpFormatter

LOCAL_PATH = str(Path("~/.local/bin/").expanduser())
if LOCAL_PATH not in os.get_exec_path():
    if "PATH" not in os.environ or len(os.environ["PATH"]) == 0:
        os.environ["PATH"] = LOCAL_PATH
    os.environ["PATH"] += (":" + LOCAL_PATH)

BENCHMARKS = "data/benchmarks.csv"
ROOT = Path(os.path.dirname(os.path.abspath(__file__)))
OUTPUT = ROOT / "output"
DATA = ROOT / "data"
PATCHES = DATA / "patches"
SRC_FOLDER = "benchmark"
SCRIPTS = ROOT / "scripts"
TARGETS = [
    "initial",
    "initial+jinline",
    "initial+jinline+jshrink",
    "initial+jinline+jshrink+jreduce"
]
ALL_TARGETS = [
    "initial",
    "initial+jinline",
    "initial+jshrink",
    "initial+jreduce",
    "initial+jinline+jshrink",
    "initial+jinline+jreduce",
    "initial+jshrink+jreduce",
    "initial+jinline+jshrink+jreduce"
]


def invoke(tools):
    if(os.path.exists(str(OUTPUT / "all.csv"))):
        return

    benchmarks = get_benchmarks()

    if len(tools) == 0:  # run all 3 tools if `tools` is not specified
        tools = ['jinline', 'jshrink', 'jreduce']
    if tools[0] != 'initial':
        tools.insert(0, 'initial')

    for benchmark in benchmarks:
        download_benchmark(benchmark)
        apply_patch(benchmark)

        src_dir = OUTPUT / benchmark.id / SRC_FOLDER
        for tool in tools:  # then run tools in sequence
            src_dir = run_tool(benchmark, src_dir, tool)

    write_stats(benchmarks, tools)


def setup(tools):
    if not shutil.which('javaq'):
        # javaq has not been set up yet. Set it up.
        setup_javaq()
    if len(tools) == 0:
        setup_jinline()
        setup_jshrink()
        setup_jreduce()

    for tool in tools:
        if tool == 'jinline':
            setup_jinline()
        elif tool == 'jshrink':
            setup_jshrink()
        elif tool == 'jreduce':
            setup_jreduce()
        else:
            pass


def clean(tools):
    for tool in tools:
        if tool == 'output':
            p = Path('output')
            if p.exists():
                shutil.rmtree(str(p))
        elif tool == 'jinline':
            p = Path('tools/jinline/build/inliner.jar')
            if p.exists():
                p.unlink()
            p = Path('output/db.sqlite3')
            if p.exists():
                p.unlink()
        else:
            pass


def write_stats(benchmarks, tools):
    stats = []
    for benchmark in benchmarks:
        target = tools[0]
        with open(str(OUTPUT / benchmark.id / target / 'stats.csv')) as f:
            stats.append(f.readlines()[-1])
        for tool in tools[1:]:
            target = target + '+' + tool
            with open(str(OUTPUT / benchmark.id / target / 'stats.csv')) as f:
                stats.append(f.readlines()[-1])

    with open(str(OUTPUT / 'all.csv'), 'w') as f:
        f.write("id,name,size,methods,classes,fields,instructions,tests\n")
        f.writelines('\n'.join(stats))


def write_target_stats(benchmarks):
    ''' WARNING: Deprecated '''
    stats = []
    for benchmark in benchmarks:
        for target in TARGETS:
            with open(str(OUTPUT / benchmark.id / target / "stats.csv")) as f:
                stats.append(f.readlines()[-1])

    with open(str(OUTPUT / "all.csv"), "w") as f:
        f.write("id,name,size,methods,classes,fields,instructions,tests\n")
        f.writelines('\n'.join(stats))


def run_tool(benchmark, src_dir, tool):
    dst_dir = src_dir.parent / (src_dir.stem + '+' + tool)
    if tool == 'initial':
        dst_dir = src_dir.parent / tool
        compile(benchmark, src_dir, dst_dir)
    elif tool == 'jinline':
        jinline(src_dir, dst_dir)
    elif tool == 'jshrink':
        jshrink(src_dir, dst_dir)
    elif tool == 'jreduce':
        jreduce(src_dir, dst_dir)

    test(dst_dir)
    metric(dst_dir)

    return dst_dir


def run_target(benchmark, target):
    ''' WARNING: Deprecated '''
    target = target.split("+")
    source = OUTPUT / benchmark.id / SRC_FOLDER

    for i in range(0, len(target)):
        t = target[i]
        dest = OUTPUT / benchmark.id / "+".join(target[0:i + 1])

        if t == "initial":
            compile(benchmark, source, dest)
        elif t == "jinline":
            jinline(source, dest)
        elif t == "jshrink":
            jshrink(source, dest)
        elif t == "jreduce":
            jreduce(source, dest)

        test(dest)
        metric(dest)

        source = dest


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
        print('Failed, while running: ', ' '.join(
            '{!r}'.format(c) for c in args), file=sys.stderr)
        # raise
        return []


def git(*cmd, work_folder="."):
    args = []
    args += ['-C', str(work_folder)]
    args += [str(c) for c in cmd]
    return read("git", *args)


def compile(benchmark, src, dest):
    if(os.path.exists(str(dest / "app.jar"))):
        return

    run([str(SCRIPTS / "benchmark.py"), str(DATA /
                                            "excluded-tests.txt"), str(src), str(dest)])


def jreduce(src, dest):
    if(os.path.exists(str(dest / "app.jar"))):
        return
    run([str(SCRIPTS / "run-jreduce.sh"), str(src), str(dest)])


def jinline(src, dest):
    if(os.path.exists(str(dest / "app.jar"))):
        return

    run([str(SCRIPTS / "run-jinline.sh"), str(src), str(dest)])


def jshrink(src, dest):
    if(os.path.exists(str(dest / "app.jar"))):
        return

    run([str(SCRIPTS / "jshrink_script.sh"), str(src), str(dest)])


def setup_jinline():
    if not os.path.exists(str(OUTPUT)):
        os.mkdir(str(OUTPUT))

    if not os.path.exists('output/db.sqlite3'):
        run(['cp', 'data/jinline/settings.py',
             'tools/jinline/src/python/settings.py'])
        with changedir('tools/jinline'):
            run(['make', 'setup'])
    with changedir('tools/jinline'):
        run(['make'])


def setup_jreduce():
    with changedir('tools/jreduce'):
        run(['stack', 'install'])


def setup_jshrink():
    with changedir('tools/jshrink/experiment_resources/jshrink-mtrace/jmtrace'):
        env = os.environ.copy()
        if 'JAVA_HOME' not in env:
            print('JAVA_HOME not set')
            sys.exit(1)
        env['JDK'] = env['JAVA_HOME']
        env['OSNAME'] = 'linux'
        run(['make'], env=env)
    with changedir('tools/jshrink/jshrink'):
        run(['mvn', 'compile', '-pl', 'jshrink-app', '-am'])
    with changedir('tools/jshrink'):
        run(['cp', 'jshrink/jshrink-app/target/jshrink-app-1.0-SNAPSHOT-jar-with-dependencies.jar',
             'experiment_resources/'])
    run(['cp', 'scripts/run_jshrink.sh',
         'tools/jshrink/experiment_resources/run_experiment_script_all_transformations_with_tamiflex_and_jmtrace.sh'])
    run(['chmod', '+x', 'tools/jshrink/experiment_resources/run_experiment_script_all_transformations_with_tamiflex_and_jmtrace.sh'])


def setup_javaq():
    with changedir('tools/javaq'):
        run(['stack', 'install'])


def test(dest):
    if(os.path.exists(str(dest / "test.txt"))):
        return

    with tempfile.TemporaryDirectory() as dirpath:
        os.chdir(dirpath)
        with open(str(dest / "test.txt"), 'w') as f:
            output = run([str(SCRIPTS / "run-test.sh"), str(dest)], stdout=f, stderr=subprocess.STDOUT)
            if output.returncode != 0:
                print("Failed, while testing", str(dest))

        os.chdir(str(ROOT))


def metric(dest):
    if(os.path.exists(str(dest / "stats.csv"))):
        return

    output = read(str(SCRIPTS / "metric.py"), str(dest))
    with open(str(dest / "stats.csv"), "w") as f:
        f.write('\n'.join(output))


def apply_patch(benchmark):
    path = OUTPUT / benchmark.id / SRC_FOLDER / "TIMESTAMP"
    patch_path = str(PATCHES / benchmark.id) + ".patch"

    if(os.path.exists(str(path))):
        return

    if(os.path.exists(str(patch_path))):
        git("apply", patch_path, work_folder=path)

    with open(str(path), 'w'):
        pass


def download_benchmark(benchmark):
    path = OUTPUT / benchmark.id / SRC_FOLDER
    if(os.path.exists(str(path / ".git" / "HEAD"))):
        return

    if(os.path.exists(str(path))):
        os.rmdir(path)

    git("clone", benchmark.url, path)
    git("checkout", "-b", "onr", benchmark.rev, work_folder=path)


def get_benchmarks():
    data = []
    with open(BENCHMARKS) as bench_file:
        reader = csv.reader(bench_file, delimiter=',')
        next(reader)  # skip header
        for row in reader:
            data.append(Benchmark(row[0], row[1], row[2]))
    return data


class Benchmark:
    def __init__(self, benchmark_id, url, rev):
        self.id = benchmark_id
        self.url = url
        self.rev = rev


def parse_args():
    parser = ArgumentParser(
        description='''Run all 3 debloat tools in sequence.
Examples:
  ./jdebloat.py setup
  ./jdebloat.py setup jinline jshrink jreduce
  ./jdebloat.py run
  ./jdebloat.py run jinline jshrink jreduce
  ./jdebloat.py clean [output, jinline]''', formatter_class=RawTextHelpFormatter)
    parser.add_argument('opt', metavar='opt', type=str,
                        nargs='?', help='[run, setup, clean]')
    parser.add_argument('tools', metavar='tools', type=str,
                        nargs='*', help='[jinline, jshrink, jreduce]')

    args = parser.parse_args()
    return args.opt, args.tools


def main():
    opt, tools = parse_args()
    if not opt or opt == 'run':
        invoke(tools)
    elif opt == 'setup':
        setup(tools)
    elif opt == 'clean':
        clean(tools)
    else:
        pass


if __name__ == "__main__":
    main()
