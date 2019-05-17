#!/usr/bin/env bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

FROM=$(realpath $1); shift
TO=$(realpath $1); shift

mkdir -p $TO

cp "$FROM/extract.json" "$FROM/test.classes.txt" "$TO" 
ln -s "$FROM/test.jar" "$TO/test.jar"
ln -s "$FROM/src" "$TO"

(cd $FROM; $SCRIPT_DIR/unjar.py join $TO/app+lib.jar app.jar lib.jar > $TO/seperation.txt)

pushd $TO

$SCRIPT_DIR/run-inliner.py $FROM/test.jar $FROM/test.classes.txt $TO/app+lib.jar $TO -o $TO/app+lib.after.jar

if [ ! -e app+lib.after.jar ]
then
    cp app+lib.jar app+lib.after.jar
fi

$SCRIPT_DIR/unjar.py split app+lib.after.jar app.jar lib.jar < seperation.txt
