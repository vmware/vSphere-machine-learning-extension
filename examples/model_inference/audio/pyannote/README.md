# Speaker diarization with pyannote.audio

`pyannote.audio` is an open-source toolkit written in Python for speaker diarization. Based on PyTorch machine learning framework, it provides a set of trainable end-to-end neural building blocks that can be combined and jointly optimized to build speaker diarization pipelines.

`pyannote.audio` also comes with pretrained models and pipelines covering a wide range of domains for voice activity detection, speaker segmentation, overlapped speech detection, speaker embedding reaching state-of-the-art performance for most of them. 


This tutorial shows you *speaker diarization* using the model with a Jupyter notebook.

Steps to run the example:

1. Create a new notebook server on **Kubeflow on vSphere** dashboard with 2 CPUs and 4G RAM using custom Docker image `projects.registry.vmware.com/models/notebook/hf-inference-deploy@sha256:8c5960ce436881f37336b12556d7a661ea20e4dbfe9ac193516cf384daa51c19`. GPU is not needed.

2. `CONNECT` to the notebook server and launch a Terminal in the created notebook server.

3. Download the Jupyter notebooks in the Terminal via command: 

   ```shell
   wget https://raw.githubusercontent.com/vmware/vSphere-machine-learning-extension/master/examples/model_inference/audio/pyannote/pyannote.ipynb
   ```

4. Visit hf.co/settings/tokens to create an access token.

5. Open the downloaded notebook and fill the created access token in cell 8 replacing "YourAccessToken".

6. Run the cells in the notebook to reproduce the results. 
