#!/usr/bin/env bash

TESTCP=$1
TEST_CLASSES=$2
APPCP=$3

if javap -cp "$APPCP:$TESTCP" org.junit.runner.JUnitCore &> /dev/null
then
    TESTCLASS=org.junit.runner.JUnitCore
elif javap -cp "$APPCP:$TESTCP" junit.textui.TestRunner &> /dev/null
then
    TESTCLASS=junit.textui.TestRunner
fi

java -cp "$APPCP:$TESTCP" $TESTCLASS $(cat $TEST_CLASSES)
