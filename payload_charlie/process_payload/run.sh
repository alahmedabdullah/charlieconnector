#!/bin/sh

INPUT_DIR=$1
OUTPUT_DIR=$2

java_exe=$(whereis java 2>&1 | awk '/java/ {print $2}')
java_path=$(dirname $java_exe)

export PATH=$java_path:$PATH



cd $INPUT_DIR

#echo $java_exe >> runlog2.txt
#echo $java_path >> runlog2.txt
#echo "/opt/charlie/tCharlie.sh $(cat cli_parameters.txt)" >> runlog2.txt

/opt/charlie/tCharlie.sh $(cat cli_parameters.txt) &> runlog.txt


cp ./*.txt ./*.ifn ../$OUTPUT_DIR

# --- EOF ---
