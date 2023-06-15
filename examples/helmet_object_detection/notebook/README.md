# Helmet Detection

AI-based helmet detection models use computer vision techniques to identify and classify objects in an image or video stream. They are designed to detect the presence of helmets on individuals and determine whether they are being worn correctly or not. The models can be trained on large datasets of helmet images and use algorithms such as YOLOv5 to analyze visual features and classify the images. The goal of such models is to improve safety in various industries by reducing the number of head injury incidents caused by not wearing helmets correctly or not wearing them at all.

## Create Notebook server on Freestone Kubeflow UI

You can refer to the [Notebook Document](https://vmware.github.io/vSphere-machine-learning-extension/user-guide/notebooks.html) to create and use a Kubeflow notebook.

- Create a Notebook Server with 1 GPU, 4CPUs, 16GB Memory and 10G volume disk


- [Python](https://www.python.org/), [PyTorch](https://pytorch.org/), and [CUDA](https://developer.nvidia.com/cuda)/[CUDNN](https://developer.nvidia.com/cudnn)  are preinstalled

## Download model and dataset

- Clone this repo in the notebook and install the dependencies in the requirements.txt:

```bash
$ !git clone https://github.com/vmware/vSphere-machine-learning-extension.git
$ cd vSphere-machine-learning-extension/examples/helmet_object_detection/notebook
$ pip install -r requirements.txt

Note:= After running above command, you will see warning like(Note: you may need to restart the kernel to use updated packages.) You can restart your Jupyter Kernel by simply clicking Kernel > Restart from the Jupyter menu. Note: This will reset your notebook and remove all variables or methods you've defined! Sometimes you'll notice that your notebook is still hanging after you've restart the kernel. If this occurs try refreshing your browser
```

- We use the VOC2007 dataset (train: *16551 images;*  val: *4952 image*) in the experiment, and you can get the data from [here](https://jhx.japaneast.cloudapp.azure.com/share/VOC2007.zip). For the data processing, the `prepare.py` converts the VOC label format (.xml) to yolo label format (.txt) and split the training and  validating data.

```bash
$ mkdir VOCdevkit
$ cd VOCdevkit

# Download the data
$ !wget https://jhx.japaneast.cloudapp.azure.com/share/VOC2007.zip
$ !unzip VOC2007.zip

$ cd ..
$ !python prepare.py
```

- Modify the configuration files <br>
  &ensp; cd to `data` folder to check the `hat.yaml`. <br>
  &ensp; cd to the `models` folder and change the `nc` parameters in `yolo5s_hat.yaml`.

```yaml
# hat.yaml
train: ./VOCdevkit/images/train/  # 16551 images
val: ./VOCdevkit/images/val/  # 4952 images

nc: 2  # number of classes
names: ["hat","person"]  # class names

# yolov5s_hat.yaml
nc: 2  # number of classes
depth_multiple: 0.33  # model depth multiple
width_multiple: 0.50  # layer channel multiple
```

## Model Training

```bash
$ !python train.py     # you can also add '--arguments' to change for your setting

YOLOv5 🚀 2021-4-12 torch 1.8.1+cu111 CUDA:0 (NVIDIA GeForce RTX 2080 Ti, 11019.5625MB)
Namespace(adam=False, artifact_alias='latest', batch_size=32, bbox_interval=-1, bucket='', cache_images=False, cfg='models/yolov5s_hat.yaml', data='data/hat.yaml', device='0', entity=None, epochs=50, evolve=False, exist_ok=False, global_rank=-1, hyp='data/hyp.scratch.yaml', image_weights=False, img_size=[640, 640], label_smoothing=0.0, linear_lr=False, local_rank=-1, multi_scale=False, name='exp', noautoanchor=False, nosave=False, notest=False, project='runs/train', quad=False, rect=False, resume=False, save_dir='runs/train/exp5', save_period=-1, single_cls=False, sync_bn=False, total_batch_size=32, upload_dataset=False, weights='yolov5s.pt', workers=8, world_size=1)
tensorboard: Start with 'tensorboard --logdir runs/train', view at http://localhost:6006/
hyperparameters: lr0=0.01, lrf=0.2, momentum=0.937, weight_decay=0.0005, warmup_epochs=3.0, warmup_momentum=0.8, warmup_bias_lr=0.1, box=0.05, cls=0.5, cls_pw=1.0, obj=1.0, obj_pw=1.0, iou_t=0.2, anchor_t=4.0, fl_gamma=0.0, hsv_h=0.015, hsv_s=0.7, hsv_v=0.4, degrees=0.0, translate=0.1, scale=0.5, shear=0.0, perspective=0.0, flipud=0.0, fliplr=0.5, mosaic=1.0, mixup=0.0
wandb: Install Weights & Biases for YOLOv5 logging with 'pip install wandb' (recommended)

                 from  n    params  module                                  arguments
  0                -1  1      3520  models.common.Focus                     [3, 32, 3]
  1                -1  1     18560  models.common.Conv                      [32, 64, 3, 2]
  2                -1  1     18816  models.common.C3                        [64, 64, 1]
  3                -1  1     73984  models.common.Conv                      [64, 128, 3, 2]
  4                -1  1    156928  models.common.C3                        [128, 128, 3]
  5                -1  1    295424  models.common.Conv                      [128, 256, 3, 2]
  6                -1  1    625152  models.common.C3                        [256, 256, 3]
  7                -1  1   1180672  models.common.Conv                      [256, 512, 3, 2]
  8                -1  1    656896  models.common.SPP                       [512, 512, [5, 9, 13]]
  9                -1  1   1182720  models.common.C3                        [512, 512, 1, False]
 10                -1  1    131584  models.common.Conv                      [512, 256, 1, 1]
 11                -1  1         0  torch.nn.modules.upsampling.Upsample    [None, 2, 'nearest']
 12           [-1, 6]  1         0  models.common.Concat                    [1]
 13                -1  1    361984  models.common.C3                        [512, 256, 1, False]
 14                -1  1     33024  models.common.Conv                      [256, 128, 1, 1]
 15                -1  1         0  torch.nn.modules.upsampling.Upsample    [None, 2, 'nearest']
 16           [-1, 4]  1         0  models.common.Concat                    [1]
 17                -1  1     90880  models.common.C3                        [256, 128, 1, False]
 18                -1  1    147712  models.common.Conv                      [128, 128, 3, 2]
 19          [-1, 14]  1         0  models.common.Concat                    [1]
 20                -1  1    296448  models.common.C3                        [256, 256, 1, False]
 21                -1  1    590336  models.common.Conv                      [256, 256, 3, 2]
 22          [-1, 10]  1         0  models.common.Concat                    [1]
 23                -1  1   1182720  models.common.C3                        [512, 512, 1, False]
 24      [17, 20, 23]  1     18879  models.yolo.Detect                      [2, [[10, 13, 16, 30, 33, 23], [30, 61, 62, 45, 59, 119], [116, 90, 156, 198, 373, 326]], [128, 256, 512]]
Model Summary: 283 layers, 7066239 parameters, 7066239 gradients, 16.5 GFLOPS

autoanchor: Analyzing anchors... anchors/target = 4.24, Best Possible Recall (BPR) = 0.9999
Image sizes 640 train, 640 test
Using 8 dataloader workers
Logging results to runs/train/exp5
Starting training for 50 epochs...

     Epoch   gpu_mem       box       obj       cls     total    labels  img_size
      0/49     2.37G   0.09416   0.08272    0.0168    0.1937       127       640: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████████| 188/188 [00:56<00:00,  3.30it/s]
               Class      Images      Labels           P           R      mAP@.5  mAP@.5:.95: 100%|███████████████████████████████████████████████████████████████████████████████████████████| 25/25 [00:21<00:00,  1.18it/s]
                 all        1590       24043       0.413       0.408       0.353       0.111
...
     Epoch   gpu_mem       box       obj       cls     total    labels  img_size
     49/49      9.2G   0.03694   0.05601 0.0003977   0.09335        63       640: 100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████| 188/188 [00:50<00:00,  3.76it/s]
               Class      Images      Labels           P           R      mAP@.5  mAP@.5:.95: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████| 25/25 [00:14<00:00,  1.71it/s]
                 all        1590       24043       0.927       0.887       0.938       0.604
                 hat        1590        1782       0.912       0.882       0.939       0.728
              person        1590       22261       0.942       0.892       0.937        0.48
50 epochs completed in 0.856 hours.
Optimizer stripped from runs/train/exp5/weights/last.pt, 14.4MB
Optimizer stripped from runs/train/exp5/weights/best.pt, 14.4MB
```

## Detect & Examples

`detect.py` runs inference on a variety of sources, using the fine-tuned model and saving results to `runs/detect`.

To run inference on example images in `VOCdevkit/images`:
```bash
$ !python detect.py --weight runs/train/exp5/weights/best.pt   --source  VOCdevkit/images/train/000004.jpg

Namespace(agnostic_nms=False, augment=False, classes=None, conf_thres=0.25, device='', exist_ok=False, img_size=640, iou_thres=0.45, name='exp', nosave=False, project='runs/detect', save_conf=False, save_txt=False, source='VOCdevkit/images/train/000003.jpg', update=False, view_img=False, weights=['runs/train/exp5/weights/best.pt'])
YOLOv5 🚀 2021-4-12 torch 1.8.1+cu111 CUDA:0 (NVIDIA GeForce RTX 2080 Ti, 11019.5625MB)

Fusing layers...
Model Summary: 224 layers, 7056607 parameters, 0 gradients, 16.3 GFLOPS
image 1/1 /root/yolov5-5.0/VOCdevkit/images/train/000003.jpg: 448x640 4 hats, 3 persons, Done. (0.022s)
Results saved to runs/detect/exp3
Done. (0.034s)
```

![Image text](./imgs/result.jpg)

## Reference

- [yolov5](https://github.com/ultralytics/yolov5)
