# DeepLab

Deeplabv3-ResNet is constructed by a Deeplabv3 model using a ResNet-50 or ResNet-101 backbone. Deeplabv3-MobileNetV3-Large is constructed by a Deeplabv3 model using the MobileNetV3 large backbone. The pre-trained model has been trained on a subset of COCO train2017, on the 20 categories that are present in the Pascal VOC dataset.

This tutorial guides you to run the model with a Jupyter notebook to show its capability of image segmentation.

Steps to run the example:

1. Create a new notebook server on **Kubeflow on vSphere** dashboard with 1 CPUs and 2G RAM using custom Docker image `projects.registry.vmware.com/models/notebook/inference:cv-pytorch-cpu-v3`. GPU is not needed. 

2. `CONNECT` to the notebook server and launch a Terminal in the created notebook server.

3. Download the Jupyter notebook in the Terminal via command: 

   ```shell
   wget https://raw.githubusercontent.com/vmware/vSphere-machine-learning-extension/master/examples/model_inference/cv/deeplab/DeepLab.ipynb
   ```

4. Open the downloaded notebook and run the cells in the notebook step-by-step to reproduce the results.
