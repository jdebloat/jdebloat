#!/bin/bash

#Full path please
app_jar=$1
lib_jar=$2
test_jar=$3
src_dir=$4
new_maven_dir=$5

cd ${new_maven_dir}/target/classes
rm "${app_jar}" && jar cf "${app_jar}" ./*
rm -rf "${new_maven_dir}"
