'''
This Python scripts takes in the Wiretap output and generates the
core methods file for Jreduce
'''

import sys
import csv

WIRETAP_METHODS_OUTPUT = sys.argv[1]
CLASSES_TO_SKIP = ["java/","jdk/", "sun/", "null.", "org/junit/", "com/sun/", "edu/ucla/pls/wiretap/", "junit/"]

with open(WIRETAP_METHODS_OUTPUT) as fp:
    lines = [line.rstrip() for line in fp]
    for line in lines:
        # Skip the standard library classes, and some others
        std_lib_class = False
        for prefix in CLASSES_TO_SKIP:
            #print(prefix)
            #print(classname)
            if line.startswith(prefix):
                std_lib_class = True
        if std_lib_class:
            continue
        output_line = line + "!code"
        print(output_line)
