# Debloat tool

The `debloat.jar` takes a java project and attempts to remove unused
methods and classes based on Call Graph analysis and, if specified,
[TamiFlex](https://doi.org/10.1145/1985793.1985827) reflection call 
analysis.

## Technical Details

The Debloat tool works by generating a call graph of the input program.
It then proceeds to remove methods that are not utilized within it. The 
user is required to specify entry points to this call graph. We provide
 three pre-programmed options : all main methods, all public methods 
(excluding tests), and/or all JUnit Tests. The user may also specify custom 
entry point/points if required.

Using the 
[Soot Bytecode optimization framework
](https://doi.org/10.1145/1925805.1925818) 
we wipe unused methods. The user has the option of either 
completely removing the method, removing the method's body, or 
replacing the method's body with a RuntimeException.

Due to 
[Java's Reflection functionality
](https://en.wikipedia.org/wiki/Reflection_(computer_programming)#Java)
Spark is incapable of creating a complete call graph. To overcome this
we use [TamiFlex](https://doi.org/10.1145/1985793.1985827). TamiFlex
observes the execution of a Java program and notes the reflective
method invocations (their locations within the Java application, and
what they invoke).

Our Debloat tool runs TamiFlex with the target Java project's tests as
input. We then extract all the method invocations achieved via
reflection. We set these as entry points for the  call graph
analysis. This thereby results in a safer debloating. 

## Usage

To execute our debloat tool with the benchmarks provided, simply run
`make debloat` in the VM provided. The debloated programs, can be found in
`output/debloat`.

If running the tool independently directory is required, please read the 
follwing usage notes:

```
usage: debloat.jar [-a <arg>] [-c <arg>] [-d] [-e <Exception Message>] [-f
       <TamiFlex Jar>] [-h] [-i <arg>] [-k] [-l <arg>] [-m] [-n <arg>]
       [-o] [-p] [-r] [-s] [-t <arg>] [-u] [-v]

An application to get the call-graph analysis of an application and to
wipe unused methods

 -a,--app-classpath <arg>                     The application classpath
 -c,--custom-entry <arg>                      Specify custom entry points
                                              in syntax of
                                              '<[classname]:[public?]
                                              [static?] [returnType]
                                              [methodName]([args...?])>'
 -d,--debug                                   Run the program in 'debug'
                                              mode. Used for testing
 -e,--include-exception <Exception Message>   Specify if an exception
                                              message should be included
                                              in a wiped method (Optional
                                              argument: the message)
 -f,--tamiflex <TamiFlex Jar>                 Enable TamiFlex
 -h,--help                                    Help
 -i,--ignore-classes <arg>                    Specify class/classes that
                                              should not be delete or
                                              modified
 -k,--use-spark                               Use Spark (Uses CHA by
                                              default)
 -l,--lib-classpath <arg>                     The library classpath
 -m,--main-entry                              Include the main method as
                                              the entry point
 -n,--maven-project <arg>                     Instead of targeting using
                                              lib/app/test classpaths, a
                                              Maven project directory may
                                              be specified
 -o,--remove-classes                          Remove unused classes
 -p,--prune-app                               Prune the application
                                              classes as well
 -r,--remove-methods                          Run remove methods (by
                                              default, the bodies are
                                              wiped and replaced by
                                              RuntimeExceptions)
 -s,--test-entry                              Include the test methods as
                                              entry points
 -t,--test-classpath <arg>                    The test classpath
 -u,--public-entry                            Include public methods as
                                              entry points
 -v,--verbose                                 Run the program in 'verbose'
                                              mode. Outputs methods
                                              analysed and methods touched
``` 

Some current restrictions:

* There must be an entry point specified.
* At present, the `--tamiflex` option only works when targeting a
   Maven Project.
* If the `--tamiflex` option is specified, the `--test-entry` option is
   automatically set (tamiflex uses tests as entry points to analyze
   reflective calls).
* `debloat.jar` only works with Java 1.8.
* `--use-spark` will use [Spark Call Graph
analysis](https://doi.org/10.1007/3-540-36579-6_12). Spark is not as
conservative an analysis as our default call graph analysis (CHA)  and 
may cause errors (we know of instances where Spark does not produce a 
complete call graph).
* We do not take into account methods accessed via Java Lambda
  Expressions. Therefore, it is possible we remove methods that are used
by the tool.

## Example usage case 1: Maven project, all entry points, with Tamiflex

`java -jar debloat.jar --maven-project <PROJECT_DIR> --public-entry 
--main-entry --test-entry --prune-app --remove-methods --tamiflex
<TAMFLEX_JAR>`

`--maven-project <PROJECT_DIR>` specifies the Maven project to be debloated.

`--public-entry --main-entry --test-entry` states that all entry points
(all public, the main methods, and test methods) should be used as entry
points to generate the call graph.

`--prune-app` specifies that that the application code should be
debloated as well as the dependency code.

`--remove-methods` specifies that methods should be removed in their
entirety. By default, only their bodies are removed.

`--tamiflex <TAMIFLEX_JAR>` specifies that TamiFlex should be used to find 
reflective calls. The argument is the location of the TamiFlex Jar.

## Example usage case 2: Non-Maven Project, main entry point, without Tamiflex

`java -jar debloat.jar --app-classpath <APP_CLASSPATH> --lib-classpath
<LIBRARY_CLASSPATH> --test-classpath <TEST_CLASSPATH>
--include-exception "ERROR, METHOD REMOVED"`

`--app-classpath <APP_CLASSPATH> --lib-classpath<LIBRARY_CLASSPATH> 
--test-classpath <TEST_CLASSPATH>` specifies the application, library,
and test classpaths of the target.

`--include-exception "ERROR, METHOD REMOVE"` specifies that when a
method's body is wiped it should be replaced with a Runtime exception
with the message "ERROR, METHOD REMOVE".

## Example usage case 4:  Maven project, with Spark, remove unused class

`java -jar debloat.jar --maven-project <PROJECT_DIR> --main-entry
--remove-classes --use-spark`

`--remove-classes` specifies that classes in which all methods are
removed, and contain no accessible static methods, are to be removed
completely.

`--use-spark` specifies that Spark Call Graph analysis is to be used.
