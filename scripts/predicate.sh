#!/usr/bin/env bash
# predicate script for jreduce to validate its intermediate results.
FOLDER=$(realpath $1);shift
REDUCED_OUTPUT=$(realpath $1);shift
#WORK_DIR=$(pwd)
#SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
SCRIPT_DIR=$(realpath $(dirname "$0"))

echo $SCRIPT_DIR
# generate jar file from input directory.
#( cd $REDUCED_OUTPUT && jar cf $WORK_DIR/app+lib.jar . )

if [ ! -L "src" ]
then
    ln -s $FOLDER/src src
fi

MYCLASSPATH=$(realpath $REDUCED_OUTPUT)

# override MYCLASSPATH with the intermediate jar file.
$SCRIPT_DIR/run-test.sh $FOLDER $MYCLASSPATH
