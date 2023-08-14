# ALBERT

[ALBERT](https://arxiv.org/abs/1909.11942) is a transformers model pretrained on a large corpus of English data in a self-supervised fashion. ALBERT was proposed by Google. ALBERT can be used to accomplish these 2 tasks:
- Taking a sentence with less than 15% of the words masked, ALBERT can predict the masked words;
- Given two sentences, ALBERT can predict the order of them. 
ALBERT can only handle English input.

This tutorial guides you to deploy the ALBERT model with torchserve to provide prediction service for the first task mentioned above.

## 1. Create a new Notebook Server

On the Kubeflow UI, create a new Notebook server with 2 CPUs, 4Gi memory, 10Gi Workspace volume.

Check the 'Custom Image' box and use this Custom Image:
```
projects.registry.vmware.com/models/notebook/serve:pytorch-cpu-v3
```

## 2. Connect to the Notebook Server

Connect to the notebook server, open a Terminal window, run this command to get the code of this project.

```
git clone https://github.com/vmware/vSphere-machine-learning-extension.git
```
Change directory to vSphere-machine-learning-extension/examples/model_serving/nlp/albert/

## 3. Download the model

Download the ALBERT model by running this command:

```shell
bash get_model.sh
```

NOTE: In case the model could not be downloaded successfully with the command above, manually download them from https://huggingface.co/albert-base-v2/tree/main and put all model files in `./albert` directory

Finally, The model directory structure should be like this:

```text
./albert
├── README.md
├── config.json
├── flax_model.msgpack 
├── model.safetensors 
├── pytorch_model.bin 
├── rust_model.ot 
├── spiece.model
├── tf_model.h5 
├── tokenizer.json
└── with-prefix-tf_model.h5
```

## 4. Install Python Packages

Install the python packages necessary for the service, listed in `requirements.txt`.

```shell
pip install -r requirements.txt
```

## 5. Create TorchServe Model Archiver File

```shell
bash create_mar.sh
```

## 6. Start TorchServe Service

Now you can start the torchserve service with below command.

```shell
bash start_ts.sh
```

## 7. Test the Service

Open another terminal window. Request the service in the terminal, execute

```shell
python test.py
```

After a while, you will see the output of the model in the terminal.

