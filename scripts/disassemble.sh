#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

TOOL=$1; shift
PROJ=$1; shift

BEFORE_JAR="${SCRIPT_DIR}/../output/${PROJ}/initial/app.jar"
AFTER_JAR="${SCRIPT_DIR}/../output/${PROJ}/initial+${TOOL}/app.jar"

deassemble() {
    JAR=$1
    # Loop through the classes (everything ending in .class)
    class_list=$(jar -tf $JAR | grep '.class' | sort)
    for class in "${class_list[@]}"; do
        # Replace /'s with .'s
        class=${class//\//.};
        # javap
        javap -classpath $JAR ${class//.class/};
    done
}

deassemble ${BEFORE_JAR} > before
deassemble ${AFTER_JAR} > after

vimdiff before after
