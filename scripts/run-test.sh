#!/usr/bin/env bash

FOLDER=$(realpath $1);shift
MYCLASSPATH=${1:-$FOLDER/app.jar:$FOLDER/lib.jar};shift
ln -s $FOLDER/src src

TESTPATH=$FOLDER/test.jar:$MYCLASSPATH

if javap -cp "$TESTPATH" org.junit.runner.JUnitCore &> /dev/null
then
    java -cp "$TESTPATH" org.junit.runner.JUnitCore $(cat $FOLDER/test.classes.txt)
elif javap -cp "$TESTPATH" junit.textui.TestRunner &> /dev/null
then
    java -cp "$TESTPATH" junit.textui.TestRunner $(cat $FOLDER/test.classes.txt)
else
    exit -1
# elif javap -cp "$APPCP:$TESTCP" org.junit.jupiter.engine.JupiterTestEngine &> /dev/null
# then
#     TESTCLASS=org.junit.jupiter.engine.JupiterTestEngine
fi
