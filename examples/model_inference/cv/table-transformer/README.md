# Table Transformer

Table Transformer is actually a DETR model - by Microsoft Research (which is part of Transformers) to perform table detection and table structure recognition on documents.

"DETR is short for DEtection TRansformer, and consists of a convolutional backbone (ResNet-50 or ResNet-101) followed by an encoder-decoder Transformer. It can be trained end-to-end to perform object detection (and panoptic segmentation). The main contribution of DETR is its simplicity: compared to other models like Faster R-CNN and Mask R-CNN, which rely on several highly engineered things like region proposals, non-maximum suppression procedure and anchor generation, DETR is a model that can simply be trained end-to-end, and fine-tuned just like you would fine-tune BERT. This is possible due to the use of a clever loss function, the so-called bipartite matching loss." 

This tutorial guides you to run the Table Transformer model with [this Jupyter notebook](https://github.com/NielsRogge/Transformers-Tutorials/blob/master/Table%20Transformer/Using_Table_Transformer_for_table_detection_and_table_structure_recognition.ipynb).

Steps to run the example:

1. Create a new notebook server on **Kubeflow on vSphere** dashboard with 1 CPU and 4G RAM using custom Docker image `projects.registry.vmware.com/models/notebook/inference:cv-pytorch-cpu-v3`. GPU is not needed. 

2. `CONNECT` to the notebook server and launch a Terminal in the created notebook server.

3. Download the [Jupyter notebook](https://github.com/NielsRogge/Transformers-Tutorials/blob/master/Table%20Transformer/Using_Table_Transformer_for_table_detection_and_table_structure_recognition.ipynb) (hash value is`c95e0a9` in case updated version doesn't work and you need to use this version) in the Terminal via command: 

   ```shell
   wget https://raw.githubusercontent.com/NielsRogge/Transformers-Tutorials/master/Table%20Transformer/Using_Table_Transformer_for_table_detection_and_table_structure_recognition.ipynb
   ```

4. Open the downloaded notebook file.

5. (Optional) Remove option `-q` from the following two cells in order to see the installation processes are completed and the modules are installed successfully:

   - `!pip install -q git+https://github.com/huggingface/transformers.git`
   - `!pip install -q timm`

6. Follow the remaining steps in the notebook to reproduce the results.

**Note：**When you run a cell to download model or data from Hugging Face, If you meet a problem like `SSLError: (MaxRetryError("HTTPSConnectionPool(host='huggingface.co', port=443):`, just run it again. Sometimes, you might need to run multiple times to get it done.
