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
temp_maven_dir=$(mktemp /tmp/XXXX)
rm ${temp_maven_dir}

${SCRIPT_DIR}/run-jshrink.sh "${TO}/app.jar" \
	"${TO}/lib.jar" "${TO}/test.jar" \
	"${TO}/src" "${temp_maven_dir}"
