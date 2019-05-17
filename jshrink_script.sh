#!/bin/bash

# Note: Expect input directory in the following format:
# ${input_dir}:
# --- extract.json
# --- test.classes.txt
# --- jars:
# --- --- app.jar
# --- --- test.jar
# --- --- lib.jar
#
# The ${input_dir} will be created and of the same format as the
# ${output_dir}

input_dir=$1
output_dir=$2
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

cp -r "${input_dir}" "${output_dir}"
temp_maven_dir=$(mktemp /tmp/XXXX)
rm ${temp_maven_dir}

${DIR}/scripts/run_jshrink.sh "${output_dir}/jars/app.jar" \
	"${output_dir}/jars/lib.jar" "${output_dir}/jars/test.jar" \
	"${temp_maven_dir}"
