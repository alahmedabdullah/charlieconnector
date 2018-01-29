#!/bin/sh

INPUT_DIR=$1
cp run.sh_template $INPUT_DIR/run.sh_template

cd $INPUT_DIR
sh ./run.sh $@

# --- EOF ---
