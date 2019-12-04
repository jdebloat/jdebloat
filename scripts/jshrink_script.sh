#!/bin/bash

# Note: Expect input directory in the following format:
# ${FROM}:
# --- app.jar
# --- test.jar
# --- lib.jar
# --- src
# --- ...
#
# The ${FROM} will be created and of the same format as the ${TO}.

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

FROM=$(realpath $1); shift
TO=$(realpath $1); shift

cp -r "${FROM}" "${TO}"
rm "${TO}/stats.csv"
temp_maven_dir=$(mktemp /tmp/XXXX)
rm ${temp_maven_dir}

${SCRIPT_DIR}/../tools/jshrink/experiment_resources/run_experiment_script_all_transformations_with_tamiflex_and_jmtrace.sh "${FROM}" "${TO}" "${temp_maven_dir}"
