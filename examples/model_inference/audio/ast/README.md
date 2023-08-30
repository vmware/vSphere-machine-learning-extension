# Audio Spectrogram Transformer

The Audio Spectrogram Transformer model was proposed in [AST: Audio Spectrogram Transformer](https://arxiv.org/abs/2104.01778) by Yuan Gong, Yu-An Chung, James Glass. The Audio Spectrogram Transformer applies a [Vision Transformer](https://huggingface.co/docs/transformers/main/en/model_doc/vit) to audio, by turning audio into an image (spectrogram). The model obtains state-of-the-art results for audio classification.

The abstract from the paper is the following:

In the past decade, convolutional neural networks (CNNs) have been widely adopted as the main building block for end-to-end audio classification models, which aim to learn a direct mapping from audio spectrograms to corresponding labels. To better capture long-range global context, a recent trend is to add a self-attention mechanism on top of the CNN, forming a CNN-attention hybrid model. However, it is unclear whether the reliance on a CNN is necessary, and if neural networks purely based on attention are sufficient to obtain good performance in audio classification. In this paper, we answer the question by introducing the Audio Spectrogram Transformer (AST), the first convolution-free, purely attention-based model for audio classification. We evaluate AST on various audio classification benchmarks, where it achieves new state-of-the-art results of 0.485 mAP on AudioSet, 95.6% accuracy on ESC-50, and 98.1% accuracy on Speech Commands V2.

This tutorial shows you the *Audio Classification* capability of this model with a Jupyter notebook.

Steps to run the example:

1. Create a new notebook server on **Kubeflow on vSphere** dashboard with 2 CPUs and 4G RAM using custom Docker image `projects.registry.vmware.com/models/notebook/hf-inference-deploy@sha256:8c5960ce436881f37336b12556d7a661ea20e4dbfe9ac193516cf384daa51c19`. GPU is not needed. 

2. `CONNECT` to the notebook server and launch a Terminal in the created notebook server.

3. Download the [Jupyter notebook](https://github.com/NielsRogge/Transformers-Tutorials/blob/master/Table%20Transformer/Using_Table_Transformer_for_table_detection_and_table_structure_recognition.ipynb) (hash value is`c95e0a9` in case updated version doesn't work and you need to use this version) in the Terminal via command: 

   ```shell
   wget https://raw.githubusercontent.com/NielsRogge/Transformers-Tutorials/master/Table%20Transformer/AST/Inference_with_the_Audio_Spectogram_Transformer_to_classify_audio.ipynb
   ```

4. Open the downloaded notebook and run the cells in the notebook to reproduce the results.
