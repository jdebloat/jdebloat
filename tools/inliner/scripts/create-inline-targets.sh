#!/bin/bash

project=$1
input_xml=$2
out_file=$3

cd `dirname $0`/../src/python
source venv/bin/activate
python3 manage.py importlogcompilation $project $input_xml $input_xml
python3 manage.py exportlogcompilation $project $out_file
