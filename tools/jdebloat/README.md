# JDebloat

JDebloat takes a java project as input and removes uninvoked methods 
and classes based on static and dynamic call graph analysis. In order 
to identify call targets invoked using Java reflection, JDebloat uses 
[TamiFlex reflection call
analysis](https://doi.org/10.1145/1985793.1985827).


**Warning :** This tool is still under development. We present this tool
with no guarantees of correctness or stability.

## Technical Details

JDebloat works by generating a static call graph of an input program. It
proceeds to remove methods that are not used based on static call graph
analysis. When using JDebloat, the user is required to specify entry
points for constructing the call graph. JDebloat provides three
pre-programmed options: (1) all main methods, (2) all public methods
(excluding tests), and/or (3) all JUnit Tests. The user may also specify
custom entry points if required.

Using the 
[Soot Bytecode optimization framework
](https://doi.org/10.1145/1925805.1925818), we remove unused Java 
bytecode methods. The user has the option of either 
completely removing the method, removing the method's body, or 
replacing the method's body with a RuntimeException.

Due to 
[Java's Reflection functionality
](https://en.wikipedia.org/wiki/Reflection_(computer_programming)#Java)
we are incapable of creating a complete call graph with standard call
graph analysis libraries alone. To overcome this
we use [TamiFlex](https://doi.org/10.1145/1985793.1985827). TamiFlex
observes the execution of a Java program under the given test suite
and notes the reflective method invocations --- where these reflective calls are made within a
Java application, and what are the call targets.

JDebloat runs TamiFlex with the target Java project's existing test
cases as input. We then extract all method invocations that were made
via reflection. We set these as additional entry points for the static
call graph analysis. This thereby results in safer debloating.

## Current Restrictions and Limitations

1. JDbloat works only with Java 1.8.
2. It requires a user to specify an entry point.
3. Handling reflective calls using Tamiflex is enabled for Maven projects
only. In other words, the `--tamiflex` option works only works when
targeting a Maven Project.
4. If the `--tamiflex` option is specified, the `--test-entry` option is
automatically set, since Tamiflex uses tests as entry points to analyze
reflective calls.
5. `--use-spark` will use the  [Spark Call Graph
analysis](https://doi.org/10.1007/3-540-36579-6_12). Spark is not as
conservative as the default call graph analysis (
[CHA](https://doi.org/10.1007/3-540-49538-X_5)) and may cause errors
(we know of instance where Spark does not produce a complete call graph).
6. We do not take into account methods accessed via Lambda Expressions.
Therefore, it is possible we may unsafely remove methods that are invoked
via lambda expressions.

## Usage

To execute the JDebloat tool with the benchmarks, simply run
`make jdebloat` in the VM provided. The debloated programs, can be found in
`output/jdebloat`, along with a a summary of the size reduction achieved
in `output/jdebloat/<BENCHMARK>/size_info.dat`.

If running the tool independently is required, please read the 
following usage notes:

```
usage: jdebloat.jar [-a <arg>] [-c <arg>] [-d] [-e <Exception Message>]
       [-f <TamiFlex Jar>] [-h] [-i <arg>] [-k] [-l <arg>] [-m] [-n <arg>]
       [-o] [-p] [-r] [-s] [-t <arg>] [-u] [-v]
An application to get the call-graph analysis of an application and to
wipe unused methods
 -a,--app-classpath <arg>                     Specify the application
                                              classpath
 -c,--custom-entry <arg>                      Specify custom entry points
                                              in syntax of
                                              '<[classname]:[public?]
                                              [static?] [returnType]
                                              [methodName]([args...?])>'
 -d,--debug                                   Run JDebloat in 'debug'
                                              mode. Used for testing
 -e,--include-exception <Exception Message>   Specify if an exception
                                              message should be included
                                              in a wiped method (Optional
                                              argument: the message)
 -f,--tamiflex <TamiFlex Jar>                 Enable TamiFlex
 -h,--help                                    Help
 -i,--ignore-classes <arg>                    Specify classes that should
                                              not be delete or modified
 -k,--use-spark                               Use Spark call graph
                                              analysis (Uses CHA by
                                              default)
 -l,--lib-classpath <arg>                     Specify the classpath for
                                              libraries
 -m,--main-entry                              Include the main method as
                                              an entry point
 -n,--maven-project <arg>                     Instead of targeting using
                                              lib/app/test classpaths, a
                                              Maven project directory may
                                              be specified
 -o,--remove-classes                          Remove unused classes
 -p,--prune-app                               Prune the application
                                              classes as well
 -r,--remove-methods                          Remove methods header and
                                              body (by default, the bodies
                                              are wiped)
 -s,--test-entry                              Include the test methods as
                                              entry points
 -t,--test-classpath <arg>                    Specify the test classpath
 -u,--public-entry                            Include public methods as
                                              entry points
 -v,--verbose                                 Run JDebloat in 'verbose'
                                              mode. Outputs analysed
                                              methods and touched methods
``` 

## Example usage case 1: Maven project, all entry points, with Tamiflex

`java -jar jdebloat.jar --maven-project <PROJECT_DIR> --public-entry 
--main-entry --test-entry --prune-app --remove-methods --tamiflex
<TAMFLEX_JAR>`

`--maven-project <PROJECT_DIR>` specifies the Maven project to be debloated.

`--public-entry --main-entry --test-entry` states that all entry points
(all public, the main methods, and test methods) should be used as entry
points to generate the call graph.

`--prune-app` specifies that that the application code should be
debloated as well as the library code.

`--remove-methods` specifies that methods should be removed in their
entirety. By default, only their bodies are removed.

`--tamiflex <TAMIFLEX_JAR>` specifies that TamiFlex should be used to find 
reflective calls. The argument is the location of the TamiFlex Jar.

## Example usage case 2: Non-Maven Project, main entry point, without Tamiflex

`java -jar jdebloat.jar --app-classpath <APP_CLASSPATH> --lib-classpath
<LIBRARY_CLASSPATH> --test-classpath <TEST_CLASSPATH>
--include-exception "ERROR, METHOD REMOVED"`

`--app-classpath <APP_CLASSPATH> --lib-classpath<LIBRARY_CLASSPATH> 
--test-classpath <TEST_CLASSPATH>` specifies the application, library,
and test classpaths of the target.

`--include-exception "ERROR, METHOD REMOVE"` specifies that when a
method's body is wiped it should be replaced with a Runtime exception
with the message "ERROR, METHOD REMOVE".

## Example usage case 4:  Maven project, with Spark, remove unused class

`java -jar jdebloat.jar --maven-project <PROJECT_DIR> --main-entry
--remove-classes --use-spark`

`--remove-classes` specifies that classes in which all methods are
removed, and contain no accessible static methods, are to be removed
completely.

`--use-spark` specifies that Spark Call Graph analysis should be used.

## Results

Running our tool on the benchmarks yields the following result.

Benchmark | Size Before Debloat (Bytes) | Size After Debloat (Bytes) | Reduction
--- | --- | ---
JavaPoet | 234746 | 230375 | 1.86%
DiskLruCache | 39107 | 39107 | 0.00%
JavaVerbalExpressions | 14746 | 14746 | 0.00%
Curator | 10427613 | 8071252 | 22.60%
JUnit4 | 811614 | 792052 | 2.41%
Qart4j | 3681396 | 1878091 | 48.98%
RxRelay | 5108491 | 4574410 | 10.45%

## Method wiping

In our tool, the default behaviour is to wipe the method body. We show
below an example of a Java method in the [Jimple
](https://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.58.7708)
format

```
.method public static staticShortMethodNoParams()Ljava/lang/Short;
    .limit stack 2
    .limit locals 1
    getstatic java/lang/System/out Ljava/io/PrintStream;
    astore_0
    aload_0
    ldc "staticShortMethodNoParams touched"
    invokevirtual java/io/PrintStream/println(Ljava/lang/String;)V
    iconst_3
    invokestatic java/lang/Short/valueOf(S)Ljava/lang/Short;
    astore_0
    aload_0
    areturn
.end method
```

After this method's body is wiped, the Jimple looks like:

```
.method public static staticShortMethodNoParams()Ljava/lang/Short;
    .limit stack 1
    .limit locals 0
    aconst_null
    areturn
.end method
```
