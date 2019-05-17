#!/usr/bin/env bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

FROM=$(realpath $1); shift
TO=$(realpath $1); shift

mkdir -p $TO/jars

cp "$FROM/extract.json" "$FROM/test.classes.txt" "$TO" 
ln -s "$FROM/test.jar" "$TO/test.jar"
ln -s "$FROM/src" "$TO"

(cd $FROM; $SCRIPT_DIR/unjar.py join $TO/app+lib.jar app.jar lib.jar > $TO/seperation.txt)

pushd $TO

mkdir -p _jreduce/output

jreduce $@\
  --work-folder "_jreduce/workfolder" \
  --cp "test.jar" \
  --target "app+lib.jar" \
  --core "@test.classes.txt" \
  -o "_jreduce/output" \
  $(realpath "$SCRIPT_DIR/run-test.sh") \
  $(realpath "$TO")

(cd _jreduce/output && jar cf ../../app+lib.after.jar *)

if [ ! -e app+lib.after.jar ]
then
    cp app+lib.jar app+lib.after.jar
fi

$SCRIPT_DIR/unjar.py split app+lib.after.jar app.jar lib.jar < seperation.txt
