#!/bin/bash

PWD="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
#PROJ_ID=$1
FROM=$1
TO=$2
temp_maven_dir=$3
WORK_LIST="${PWD}/work_list.dat"
PROJECT_DIR="${PWD}/../../../output"
DEBLOAT_APP="${PWD}/jshrink-app-1.0-SNAPSHOT-jar-with-dependencies.jar"
SIZE_FILE="${PWD}/size_data.csv"
JAVA="/usr/bin/java"
TAMIFLEX="${PWD}/poa-2.0.3.jar"
JSHRINK_MTRACE="${PWD}/jshrink-mtrace"
JMTRACE="${JSHRINK_MTRACE}/jmtrace"
MTRACE_BUILD="${JSHRINK_MTRACE}/build"
TIMEOUT=54000 #15 hours
LOG_DIR="${PWD}/output_log"
OUTPUT_LOG_DIR="${LOG_DIR}/all_transformations_with_tamiflex_and_jmtrace_output_log"

if [ ! -f "${JAVA}" ]; then
	>&2 echo "Could not find Java 1.8 at the specified path: "${JAVA}
	>&2 echo "Please update the classpath in this script."
	exit 1
fi

if [ ! -f "${TAMIFLEX}" ]; then
	>&2 echo "Could not find TamiFlex at specified path: "${TAMIFLEX}
	exit 1
fi

if [ ! -f ${SIZE_FILE} ]; then
	echo "project,using_public_entry,using_main_entry,using_test_entry,custom_entry,soot_version,is_app_prune,tamiflex,jmtrace,baseline,remove_methods,method_inliner,class_collapser,parameter_removal,class_removal,app_size_before,libs_size_before,app_size_after,libs_size_after,app_num_methods_before,libs_num_methods_before,app_num_methods_after,libs_num_methods_after,tests_run_before,tests_errors_before,tests_failed_before,tests_skipped_before,tests_run_after,tests_errors_after,tests_failed_after,tests_skipped_after,time_elapsed" >${SIZE_FILE}
else
	2>&1 echo "WARNING: size file \""${SIZE_FILE}"\" already exists. Appending to this file"
fi

if [ ! -f "${DEBLOAT_APP}" ]; then
	echo "Cannot find "${DEBLOAT_APP}
	exit 1
fi

{
	#Make jtrace
	cd "${JMTRACE}"
	make clean
	./makeit.sh
	cd ${PWD}
}&>/dev/null


item="${TO}"
item_dir="${TO}"
cd "${item_dir}"

#OUTPUT_LOG_DIR
ITEM_LOG_DIR="${OUTPUT_LOG_DIR}/${item}"

echo "Processing : "${item}

temp_file=$(mktemp /tmp/XXXX)

#Full path please
app_jar="${item_dir}/app.jar"
lib_jar="${item_dir}/lib.jar"
test_jar="${item_dir}/test.jar"
src_dir="${item_dir}/src"
new_maven_dir="${temp_maven_dir}"

DIR="${PWD}/../../../scripts"
${DIR}/prepare_for_jshrink.sh "${app_jar}" "${lib_jar}" "${test_jar}" "${src_dir}" "${new_maven_dir}"

#timeout ${TIMEOUT} ${JAVA} -Xmx20g -jar ${DEBLOAT_APP} --jmtrace "${MTRACE_BUILD}" --tamiflex ${TAMIFLEX} --maven-project ${new_maven_dir} -T --use-cache --public-entry --main-entry --test-entry --prune-app --class-collapser --inline --remove-fields --remove-methods --log-directory "${ITEM_LOG_DIR}" --verbose 2>&1 >${temp_file}
timeout ${TIMEOUT} ${JAVA} -Xmx20g -jar ${DEBLOAT_APP} --jmtrace "${MTRACE_BUILD}" --tamiflex ${TAMIFLEX} --maven-project ${new_maven_dir} -T --use-cache --public-entry --main-entry --test-entry --prune-app --class-collapser --inline --remove-fields --remove-methods --log-directory "${ITEM_LOG_DIR}" --verbose 2>&1 >${temp_file}
exit_status=$?

cp -r "${new_maven_dir}/src" "${src_dir}"
cd ${new_maven_dir}/target/classes; rm "${app_jar}" && jar cf "${app_jar}" ./*
rm -rf "${new_maven_dir}"


if [[ ${exit_status} == 0 ]]; then
	cat ${temp_file}
	echo ""
	app_size_before=$(cat "${ITEM_LOG_DIR}/log.dat" | awk -F, '($1=="app_size_before"){print $2}')
	lib_size_before=$(cat "${ITEM_LOG_DIR}/log.dat" | awk -F, '($1=="libs_size_before"){print $2}')
	app_size_after=$(cat "${ITEM_LOG_DIR}/log.dat" | awk -F, '($1=="app_size_after"){print $2}')
	lib_size_after=$(cat "${ITEM_LOG_DIR}/log.dat" | awk -F, '($1=="libs_size_after"){print $2}')
	test_run_before=$(cat "${ITEM_LOG_DIR}/log.dat" | awk -F, '($1=="tests_run_before"){print $2}')
	test_errors_before=$(cat "${ITEM_LOG_DIR}/log.dat" | awk -F, '($1=="tests_errors_before"){print $2}')
	test_failures_before=$(cat "${ITEM_LOG_DIR}/log.dat" | awk -F, '($1=="tests_failed_before"){print $2}')
	test_skipped_before=$(cat "${ITEM_LOG_DIR}/log.dat" | awk -F, '($1=="tests_skipped_before"){print $2}')
	test_run_after=$(cat "${ITEM_LOG_DIR}/log.dat" | awk -F, '($1=="tests_run_after"){print $2}')
	test_errors_after=$(cat "${ITEM_LOG_DIR}/log.dat" | awk -F, '($1=="tests_errors_after"){print $2}')
	test_failures_after=$(cat "${ITEM_LOG_DIR}/log.dat" | awk -F, '($1=="tests_failed_after"){print $2}')
	test_skipped_after=$(cat "${ITEM_LOG_DIR}/log.dat" | awk -F, '($1=="tests_skipped_after"){print $2}')
	app_num_methods_before=$(cat "${ITEM_LOG_DIR}/log.dat" | awk -F, '($1=="app_num_methods_before"){print $2}')
	lib_num_methods_before=$(cat "${ITEM_LOG_DIR}/log.dat" | awk -F, '($1=="libs_num_methods_before"){print $2}')
	app_num_methods_after=$(cat "${ITEM_LOG_DIR}/log.dat" | awk -F, '($1=="app_num_methods_after"){print $2}')
	lib_num_methods_after=$(cat "${ITEM_LOG_DIR}/log.dat" | awk -F, '($1=="libs_num_methods_after"){print $2}')
	time_elapsed=$(cat "${ITEM_LOG_DIR}/log.dat" | awk -F, '($1=="time_elapsed"){print $2}')		

	#The current settings
	using_public_entry="1"
	using_main_entry="1"
	using_test_entry="1"
	custom_entry=""
	is_app_prune="1"
	tamiflex="1"
	jmtrace="1"
	baseline="0"
	remove_methods="1"
	method_inliner="1"
	class_collapser="1"
	parameter_removal="1"
	class_removal="0"
	soot_version="3.3.0"

	echo ${item},${using_public_entry},${using_main_entry},${using_test_entry},${custom_entry},${soot_version},${is_app_prune},${tamiflex},${jmtrace},${baseline},${remove_methods},${method_inliner},${class_collapser},${parameter_removal},${class_removal},${app_size_before},${lib_size_before},${app_size_after},${lib_size_after},${app_num_methods_before},${lib_num_methods_before},${app_num_methods_after},${lib_num_methods_after},${test_run_before},${test_errors_before},${test_failures_before},${test_skipped_before},${test_run_after},${test_errors_after},${test_failures_after},${test_skipped_after},${time_elapsed} >>${SIZE_FILE}
elif [[ ${exit_status} == 124 ]];then
	echo "TIMEOUT!"
	echo "Output the following: "
			cat ${temp_file}
	echo ""
	rm -rf ${ITEM_LOG_DIR}
else
	echo "Could not properly process "${item}
	echo "Output the following: "
	cat ${temp_file}
	echo ""
	rm -rf ${ITEM_LOG_DIR}
fi


rm ${temp_file}
