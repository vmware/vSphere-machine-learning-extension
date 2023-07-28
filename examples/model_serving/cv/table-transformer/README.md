# Table Transformer

Table Transformer is actually a DETR model - by Microsoft Research (which is part of Transformers) to perform table detection and table structure recognition on documents.

"DETR is short for DEtection TRansformer, and consists of a convolutional backbone (ResNet-50 or ResNet-101) followed by an encoder-decoder Transformer. It can be trained end-to-end to perform object detection (and panoptic segmentation). The main contribution of DETR is its simplicity: compared to other models like Faster R-CNN and Mask R-CNN, which rely on several highly engineered things like region proposals, non-maximum suppression procedure and anchor generation, DETR is a model that can simply be trained end-to-end, and fine-tuned just like you would fine-tune BERT. This is possible due to the use of a clever loss function, the so-called bipartite matching loss." 

---- From [Jupyter notebook](https://github.com/NielsRogge/Transformers-Tutorials/blob/master/Table%20Transformer/Using_Table_Transformer_for_table_detection_and_table_structure_recognition.ipynb)

Steps to run the example:

1. Create a new notebook server on **Kubeflow on vSphere** dashboard with 1 CPU and 2G RAM using custom Docker image `projects.registry.vmware.com/models/notebook/inference:cv-pytorch-cpu-v1`. GPU is not needed. 
2. Download the [Jupyter notebook](https://github.com/NielsRogge/Transformers-Tutorials/blob/master/Table%20Transformer/Using_Table_Transformer_for_table_detection_and_table_structure_recognition.ipynb) (hash value is`c95e0a9` in case updated version doesn't work and you need to use this version).
3. `CONNECT` to the notebook server and upload the notebook file and open it in the notebook server.
4. Make sure the installed torch version is `2.0` or `2.0.1` as the example doesn't work with lower versions. Run `!pip install torch==2.0` or `!pip install torch==2.0.1`  in a new cell in the notebook.
5. Follow the steps in the notebook to reproduce the results.
