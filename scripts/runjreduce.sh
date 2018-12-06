#!/usr/bin/env bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

TESTCP=$1
TEST_CLASSES=$2
APPCP=$3

WORK_FOLDER=$4

jreduce -v \
    --work-folder "$WORK_FOLDER" \
    --stdlib \
    --cp "$TESTCP" \
    --target "$APPCP" \
    $(realpath "$SCRIPT_DIR/runtest.sh") \
    $(realpath "$TESTCP") $(realpath "$TEST_CLASSES")
