#set -x
#set -euo pipefail

model_name="albert"
model_path="./albert"

export TMPDIR="$(pwd)/temp"
export TEMP="$(pwd)/temp"
mkdir -p ${TMPDIR}

function create_mar_file() {
  handle_file="./handler.py"

  rm -rf logs
  temp_dir=$(mktemp -d)
#  echo ${temp_dir}
  ln -s $(pwd)/${model_path} ${temp_dir}

  mkdir -p ./model_store
  torch-model-archiver \
    --model-name ${model_name} \
    --version 1.0 \
    --handler ${handle_file} \
    --export-path ./model_store \
    --extra-files ${temp_dir} \
    --force
}

echo "Creating mar file..."
create_mar_file
echo "Mar file creation finished."
