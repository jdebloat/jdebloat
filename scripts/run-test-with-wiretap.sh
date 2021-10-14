#!/usr/bin/env bash
FOLDER=$(realpath $1);shift
MYCLASSPATH=${1:-$FOLDER/app.jar:$FOLDER/lib.jar};shift
WIRETAP=$(realpath $1);shift

if [ ! -L "src" ]
then
    ln -s $FOLDER/src src
fi


TESTPATH=$FOLDER/test.jar:$MYCLASSPATH:$WIRETAP

if javap -cp "$TESTPATH" org.junit.runner.JUnitCore &> /dev/null
then
    cd $FOLDER && java -javaagent:$WIRETAP -Dwiretap.recorder=BinaryHistoryLogger -cp "$TESTPATH" org.junit.runner.JUnitCore $(cat $FOLDER/test.classes.txt)
elif javap -cp "$TESTPATH" junit.textui.TestRunner &> /dev/null
then
    cd $FOLDER && java -javaagent:$WIRETAP -Dwiretap.recorder=BinaryHistoryLogger -cp "$TESTPATH" junit.textui.TestRunner $(cat $FOLDER/test.classes.txt)
else
    exit -1
# elif javap -cp "$APPCP:$TESTCP" org.junit.jupiter.engine.JupiterTestEngine &> /dev/null
# then
#     TESTCLASS=org.junit.jupiter.engine.JupiterTestEngine
fi

