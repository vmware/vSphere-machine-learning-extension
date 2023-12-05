#!/usr/bin/bash

#set -x

CURRENT_DIR="$(pwd)"
checkpoint_file="${CURRENT_DIR}/7B/consolidated.00.pth"
model_params_file="${CURRENT_DIR}/7B/params.json"
tokenizer_model_file="${CURRENT_DIR}/tokenizer.model"
handle_file="${CURRENT_DIR}/handler.py"

#
# Prepare extra files that should be added to the package
#
export TMPDIR="$(pwd)/temp"
export TEMP="$(pwd)/temp"
mkdir -p ${TMPDIR}
temp_dir=$(mktemp -d)

ln -s "$(pwd)/./llama" ${temp_dir}
#ln -s ${checkpoint_file} $temp_dir
ln -s ${model_params_file} $temp_dir
ln -s ${tokenizer_model_file} ${temp_dir}

#
# Start packaging
#
mkdir -p ./model_store

echo "== Started model packaging =="
model_name="llama"
start_time="$(date -u +%s)"
torch-model-archiver \
  --model-name ${model_name} \
  --version 1.0 \
  --serialized-file ${checkpoint_file} \
  --handler ${handle_file} \
  --export-path ./model_store \
  --extra-files ${temp_dir} \
  --force
end_time="$(date -u +%s)"
elapsed="$(($end_time-$start_time))"
echo "== Model packaging completed. Total $elapsed seconds elapsed =="

