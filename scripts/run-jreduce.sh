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

mkdir -p _jreduce

jreduce $@\
  --work-folder "_jreduce/workfolder" \
  --cp "test.jar" \
  --core "@test.classes.txt" \
  --jre "$JAVA_HOME/jre" \
  -S "classes" \
  -o "_jreduce/output" \
  --timelimit 1800 \
  "app+lib.jar" \
  $(realpath "$SCRIPT_DIR/predicate.sh") $(realpath "$TO") {}

# generate the output jar file only if the output folder is not empty.
if [ "$(find _jreduce/output -mindepth 1 -print -quit 2>/dev/null)" ]
then
    ( cd _jreduce/output && jar cf ../../app+lib.after.jar * )
else
# else copy the input jar file as the output.
    cp app+lib.jar app+lib.after.jar
fi

$SCRIPT_DIR/unjar.py split app+lib.after.jar app.jar lib.jar < seperation.txt
