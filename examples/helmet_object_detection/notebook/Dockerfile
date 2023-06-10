FROM ubuntu:20.04

# Downloads to user config dir
ADD https://ultralytics.com/assets/Arial.ttf https://ultralytics.com/assets/Arial.Unicode.ttf /root/.config/Ultralytics/

# Install linux packages
RUN apt update
RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt install -y tzdata
RUN apt install --no-install-recommends -y python3-pip git zip curl htop libgl1-mesa-glx libglib2.0-0 libpython3.8-dev
# RUN alias python=python3

# Install pip packages
COPY requirements.txt .
RUN python3 -m pip install --upgrade pip wheel
RUN pip install -r requirements.txt -i https://pypi.douban.com/simple/

COPY . /

# CMD tail -f /var/log/cron.log 

# CMD ["python3", "ingest_pipeline.py"]

