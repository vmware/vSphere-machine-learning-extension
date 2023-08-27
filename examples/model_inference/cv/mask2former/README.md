# Inference with Mask2Former

[Mask2Former](https://huggingface.co/docs/transformers/main/en/model_doc/mask2former) is a very nice new model from Meta AI, capable of solving any type of image segmentation (whether it's instance, semantic or panoptic segmentation) using the same architecture. The model improves upon DETR and MaskFormer by incorporating masked attention in its Transformer decoder.

This tutorial shows you with a Jupyter notebook the inference with this model (i.e. making predictions on a new image) for panoptic, semantic and instance segmentation.

Steps to run the example:

1. Create a new notebook server on **Kubeflow on vSphere** dashboard with 2 CPUs and 6G RAM using custom Docker image `projects.registry.vmware.com/models/notebook/inference:cv-pytorch-cpu-v3`. GPU is not needed. 

2. `CONNECT` to the notebook server and launch a Terminal in the created notebook server.

3. Download the Jupyter notebook in the Terminal via command: 

   ```shell
   wget https://raw.githubusercontent.com/NielsRogge/Transformers-Tutorials/master/Mask2Former/Inference_with_Mask2Former.ipynb
   ```

4. Open the downloaded notebook and run the cells in the notebook to reproduce the results.
