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
EXAMPLES = "data/examples.csv"
ROOT = Path(os.path.dirname(os.path.abspath(__file__)))
OUTPUT = ROOT / "output"
DATA = ROOT / "data"
EXAMPLES_FOLDER = ROOT / "examples"
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
TOOL_LIST = ['jinline', 'jshrink', 'jreduce']

def invoke(tools, csv_file, benchmark):
    stats_file = csv_file + '-' + benchmark + '.csv'
    if(os.path.exists(str(OUTPUT / stats_file))):
        os.remove(str(OUTPUT / stats_file))
        # return

    if len(tools) == 0:  # run all 3 tools if `tools` is not specified
        tools = ['jinline', 'jshrink', 'jreduce']
    if tools[0] != 'initial':
        tools.insert(0, 'initial')

    benchmarks = get_benchmarks(csv_file, benchmark)
    for benchmark in benchmarks:
        download_benchmark(benchmark)

        src_dir = OUTPUT / benchmark.id / SRC_FOLDER
        for tool in tools:  # then run tools in sequence
            src_dir = run_tool(benchmark, src_dir, tool)

    write_stats(benchmarks, tools, stats_file)
    read_stats(benchmarks, tools)

def setup(tools):
    if not shutil.which('javaq'):
        # javaq has not been set up yet. Set it up.
        setup_javaq()

    for tool in tools:
        if tool == 'jinline':
            setup_jinline()
        elif tool == 'jshrink':
            setup_jshrink()
        elif tool == 'jreduce':
            setup_jreduce()

def clean():
    p = Path('output')
    if p.exists():
        shutil.rmtree(str(p))

def write_stats(benchmarks, tools, output_file):
    stats = []
    for benchmark in benchmarks:
        target = tools[0]
        with open(str(OUTPUT / benchmark.id / target / 'stats.csv')) as f:
            stats.append(f.readlines()[-1])
        for tool in tools[1:]:
            target = target + '+' + tool
            with open(str(OUTPUT / benchmark.id / target / 'stats.csv')) as f:
                stats.append(f.readlines()[-1])

    with open(str(OUTPUT / output_file), 'w') as f:
        f.write("id,name,size,methods,classes,fields,instructions,tests\n")
        f.writelines('\n'.join(stats))

def read_stats(benchmarks, tools):
    class BenchmarkStat:
        def __init__(self, bid):
            self.id = bid
            self.sizes = [0, 0]
            self.tests = [0, 0]

        def print_stat(self):
            size_reduction = (self.sizes[0] - self.sizes[1]) / self.sizes[0]
            print("Benchmark {}:".format(bid))
            print("  Size before debloating: {}".format(self.sizes[0]))
            print("  Size after  debloating: {}".format(self.sizes[1]))
            print("  Size reduction: {:.2%}".format(size_reduction))
            print("  Total test cases before debloating: {}".format(self.tests[0]))
            print("  Total test cases after  debloating: {}, ({} successes, {} failures)".format(
                self.tests[1], self.tests[1], self.tests[0] - self.tests[1]))

    before = tools[0]
    after = '+'.join(tools)
    tool_chain = '->'.join(tools[1:]) # skip 'initial' phase

    print()
    print("=====================================================================")
    print("                          Debloating Stats:")
    print("=====================================================================")

    print("Using debloating tool(s): " + tool_chain)
    for benchmark in benchmarks:
        bm_stat = BenchmarkStat(benchmark.id)
        with open(str(OUTPUT / benchmark.id / before / 'stats.csv')) as f:
            items = f.readlines()[-1].split(',')
            bid, size, test = items[0], items[2], items[-1]

            bm_stat.sizes[0] = int(size)
            bm_stat.tests[0] = int(test)

        with open(str(OUTPUT / benchmark.id / after / 'stats.csv')) as f:
            items = f.readlines()[-1].split(',')
            bid, size, test = items[0], items[2], items[-1]

            bm_stat.sizes[1] = int(size)
            bm_stat.tests[1] = int(test)

        bm_stat.print_stat()

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
        # shutil.rmtree(str(dest))
        return

    run([str(SCRIPTS / "benchmark.py"), str(DATA /
                                            "excluded-tests.txt"), str(src), str(dest)])

def jreduce(src, dest):
    if(os.path.exists(str(dest / "app.jar"))):
        shutil.rmtree(str(dest))
        # return
    run([str(SCRIPTS / "run-jreduce.sh"), str(src), str(dest)])

def jinline(src, dest):
    if(os.path.exists(str(dest / "app.jar"))):
        shutil.rmtree(str(dest))
        # return

    clean_jinline_db()
    setup_jinline_db()
    run([str(SCRIPTS / "run-jinline.sh"), str(src), str(dest)])

def jshrink(src, dest):
    if(os.path.exists(str(dest / "app.jar"))):
        shutil.rmtree(str(dest))
        # return

    p = ROOT / "tools" / "jshrink" / "experiment_resources" / "size_data.csv"
    if p.exists():
        os.remove(str(p))

    run([str(SCRIPTS / "jshrink_script.sh"), str(src), str(dest)])

def setup_jinline_db():
    print("JInline: creating DB...")
    if not os.path.exists('output/db.sqlite3'):
        run(['cp', 'data/jinline/settings.py',
             'tools/jinline/src/python/settings.py'])
        with changedir('tools/jinline'):
            run(['make', 'setup'])

def clean_jinline_db():
    print("JInline: cleaning DB...")
    p = Path('output/db.sqlite3')
    if p.exists():
        os.remove(str(p))

def setup_jinline():
    if not os.path.exists(str(OUTPUT)):
        os.mkdir(str(OUTPUT))

    setup_jinline_db()
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
    if benchmark.url != "":
        if(os.path.exists(str(path / ".git" / "HEAD"))):
            return

        if(os.path.exists(str(path))):
            shutil.rmtree(str(path))

        git("clone", benchmark.url, path)
        git("checkout", "-b", "onr", benchmark.rev, work_folder=path)
        apply_patch(benchmark)
    else:  # no url provided. Search locally in `examples/` directory
        if(os.path.exists(str(path / "pom.xml"))):
            return

        if(os.path.exists(str(path))):
            shutil.rmtree(str(path))

        if not (EXAMPLES_FOLDER / benchmark.id).exists():
            print("Example project '{}' doesn't exist.".format(benchmark.id))
            return

        shutil.copytree(str(EXAMPLES_FOLDER / benchmark.id), str(path))


def get_benchmarks(csv_file, bm_name):
    file_name = str(DATA / (csv_file + ".csv"))
    if not os.path.exists(file_name):
        print("Cannot find the benchmark csv file:", str(file_name))
        sys.exit(1)

    data = []
    with open(str(file_name)) as bench_file:
        reader = csv.reader(bench_file, delimiter=',')
        next(reader)  # skip header
        for row in reader:
            row += [""] * (3 - len(row)) # fill up row with empty strings if len(row) < 3
            data.append(Benchmark(row[0], row[1], row[2]))

    if bm_name != "all":
        data = [bm for bm in data if bm.id == bm_name]
        if len(data) == 0:
            print("Project {} doesn't exist.".format(bm_name))
            sys.exit(1)

    return data

class Benchmark:
    def __init__(self, benchmark_id, url, rev):
        self.id = benchmark_id
        self.url = url
        self.rev = rev

def verify_tools(tools):
    for tool in tools:
        if tool not in TOOL_LIST:
            print('Unknown tool:', tool)
            sys.exit(1)

def parse_args():
    parser = ArgumentParser(
        description='''Run debloat tools in sequence.

Examples:
   ./jdebloat.py setup
        (setup environment for all tools)
or ./jdebloat.py setup jinline jshrink jreduce
        (essnentially the same as ./jdebloat.py setup)
or ./jdebloat.py run
        (run all tools on all benchmarks in the order of "jinline jshrink jreduce")
or ./jdebloat.py run jinline
        (run jinline only on all benchmarks)
or ./jdebloat.py run jinline jshrink jreduce
        (essnentially the same as ./jdebloat.py run)
or ./jdebloat.py run jshrink --benchmark=jshrink-test
        (run jshrink only on "jshrink-test" benchmark only)
or ./jdebloat.py clean
        (clean all debloating outputs)''', formatter_class=RawTextHelpFormatter)

    subparsers = parser.add_subparsers(dest='command')
    subparsers.required = True
    clean_parser = subparsers.add_parser('clean', help='Clean debloating outputs.')

    tools_parser = subparsers.add_parser('setup', help =
        'Setup environment for the specific tool(s).')
    tools_parser.add_argument('tools',
                               nargs='*', help=str(TOOL_LIST),
                               default=TOOL_LIST)

    run_parser = subparsers.add_parser('run', help = '''\
Run tool(s) in speficifed order.
Different orders can generate different debloating results.
The default sequence is "jinline jshrink jreduce".''')
    run_parser.add_argument('tools',
                            nargs='*',
                            help=str(TOOL_LIST),
                            default=TOOL_LIST)
    run_parser.add_argument('--csv', type = str, default = 'examples', help = '''\
Specify the <file name> of the benchmark csv file. The csv file should be put
under data/ directory and be like data/<file name>.csv.
Using data/examples.csv by default.''')
    run_parser.add_argument('-b', '--benchmark', type = str, default = 'all', help = '''\
Specify a certain project to debloat.
Debloat all benchmarks by default.''')

    args = parser.parse_args()
    if args.command != 'clean':
        verify_tools(args.tools)

    return args

def main():
    args = parse_args()
    if args.command == 'clean':
        clean()
    elif args.command == 'run':
        invoke(args.tools, args.csv, args.benchmark)
    elif args.command == 'setup':
        setup(args.tools)

if __name__ == "__main__":
    main()
