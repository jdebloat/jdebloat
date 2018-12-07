#!/usr/bin/env bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

TESTCP=$1; shift
TEST_CLASSES=$1; shift
APPCP=$1; shift

WORK_FOLDER=$1; shift

jreduce $@\
    --work-folder "$WORK_FOLDER" \
    --stdlib \
    --cp "$TESTCP" \
    --target "$APPCP" \
    $(realpath "$SCRIPT_DIR/runtest.sh") \
    $(realpath "$TESTCP") $(realpath "$TEST_CLASSES")
