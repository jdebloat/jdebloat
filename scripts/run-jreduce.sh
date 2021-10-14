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

# Run the tests and record the set of methods used
sh $SCRIPT_DIR/run-test-with-wiretap.sh $(realpath "$TO") $(realpath app+lib.jar) $SCRIPT_DIR/../libs/wiretap.jar &> /dev/null
python3 $SCRIPT_DIR/generate-jreduce-core-methods.py _wiretap/methods.txt > jreduce_core.txt

jreduce $@\
  -q \
  --work-folder "_jreduce/workfolder" \
  --jre "$JAVA_HOME/jre" \
  -S "items+logic" \
  --unsafe \
  --core "@jreduce_core.txt" \
  --stdlib "../../stdlib.bin" \
  -o "app+lib.after.jar" \
  --predicate-timelimit 180 \
  app+lib.jar \
  -- timeout 180 $(realpath "$SCRIPT_DIR/predicate.sh") $(realpath "$TO") {}

# generate the output jar file only if the output folder is not empty.
#if [ "$(find _jreduce/output -mindepth 1 -print -quit 2>/dev/null)" ]
#then
#    ( cd _jreduce/output && jar cf ../../app+lib.after.jar * )
#else
# else copy the input jar file as the output.
#    cp app+lib.jar app+lib.after.jar
#fi

$SCRIPT_DIR/unjar.py split app+lib.after.jar app.jar lib.jar < seperation.txt
