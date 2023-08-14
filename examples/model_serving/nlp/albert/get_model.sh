#set -x
#set -euo pipefail

download_model_dir="./albert"
model_hub_name="albert-base-v2"


function download_model() {
  python ./Download_model.py \
    --model_name ${model_hub_name} \
    --local_dir ./${download_model_dir}
}

download_model














