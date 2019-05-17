#!/bin/bash

#Full path please
app_jar=$1
lib_jar=$2
test_jar=$3
src_dir=$4
new_maven_dir=$5

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

${DIR}/prepare_for_jshrink.sh "${app_jar}" "${lib_jar}" "${test_jar}" "${src_dir}" "${new_maven_dir}"

TIMEOUT=18000 #Five hours
DEBLOAT_APP="${DIR}/../tools/jdebloat/jdebloat.jar"
TAMIFLEX="${DIR}/../tools/jdebloat/poa-2.0.3.jar"
LOG_DIR=$(mktemp /tmp/project_log_XXXXX)
rm "${LOG_DIR}"

timeout ${TIMEOUT} java -Xmx20g -jar ${DEBLOAT_APP} --maven-project ${new_maven_dir} --public-entry --main-entry --test-entry --prune-app --class-collapser --inline --remove-fields --remove-methods --verbose --log-directory "${LOG_DIR}"

${DIR}/jshrink_cleanup.sh "${app_jar}" "${lib_jar}" "${test_jar}" "${src_dir}" "${new_maven_dir}"
