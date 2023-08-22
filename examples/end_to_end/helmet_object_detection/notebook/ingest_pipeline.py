import os

project = "Helmet-Detection"
run_id = "1.0"
resume_run = True

import argparse
import requests, io
from zipfile import ZipFile
from urllib.request import urlopen
from io import BytesIO
import ssl
import certifi
ssl._create_default_https_context = ssl._create_unverified_context


### Declaring input arguments

parser = argparse.ArgumentParser()
parser.add_argument('--dataurl', type=str, default='https://jhx.japaneast.cloudapp.azure.com/share/VOC2007.zip')
parser.add_argument('--datapath', type=str, default='/VOCdevkit')

args = vars(parser.parse_args())

dataurl = args['dataurl']
datapath = args['datapath']

DATAURL = dataurl
DATAPATH = datapath

### Data Extraction : extract data and save to attached extenal pvc at location /VOCdevkit

def download_and_unzip(url, extract_to=DATAPATH):
    print('>>>>>>>>>>>>>>TEST')
    http_response = urlopen(url, context=ssl.create_default_context(cafile=certifi.where()))
    zipfile = ZipFile(BytesIO(http_response.read()))
    zipfile.extractall(path=extract_to)
    print("Data Archive unzipped")

print('>>>>>>>>>>>> Downloading Dataset.....')
download_and_unzip(DATAURL, DATAPATH)
print('----- DOWNLOAD COMPELETED -----')