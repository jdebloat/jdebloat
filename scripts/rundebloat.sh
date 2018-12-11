#!/bin/bash

PWD="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
DEBLOAT_TOOL_DIR="${PWD}/../tools/debloat"
TAMIFLEX="${DEBLOAT_TOOL_DIR}/poa-2.0.3.jar"
DEBLOAT="${DEBLOAT_TOOL_DIR}/debloat.jar"
BENCHMARK="$1"
SIZE_INFO_OUTPUT="$BENCHMARK/size_info.dat"

if [ -f "${SIZE_INFO_OUTPUT}" ] ; then
	>&2 echo "Benchmarks have already been processed"
	exit 1
fi

mvn -f "$BENCHMARK/pom.xml" clean 2>&1 >/dev/null

OUTPUT_FILE="$BENCHMARK/output.txt"
echo "Processing "${BENCHMARK}"..." >>${SIZE_INFO_OUTPUT}
java -Xmx4G -jar ${DEBLOAT} --maven-project "${BENCHMARK}" \
     --test-entry --public-entry --main-entry --prune-app \
     --tamiflex "${TAMIFLEX}" --verbose 2>&1 > ${OUTPUT_FILE}
echo "Done!" >>${SIZE_INFO_OUTPUT}


#Get sizes
before=$(cat ${OUTPUT_FILE} | awk -F, '($1 ~ "app_size_decompressed_before_*"){value+=$2}($1 ~ "lib_size_decompressed_before_*"){value+=$2}END{print value}')
after=$(cat ${OUTPUT_FILE} | awk -F, '($1 ~ "app_size_decompressed_after_*"){value+=$2}($1 ~ "lib_size_decompressed_after_*"){value+=$2}END{print value}')

echo "Size before (in bytes): "${before} >>${SIZE_INFO_OUTPUT}
echo "Size after (in bytes): "${after} >>${SIZE_INFO_OUTPUT}
echo "Percentage reduction: "$(echo "(${before} - ${after})*100/${before}" | bc -l) >>${SIZE_INFO_OUTPUT}
cat ${SIZE_INFO_OUTPUT}
