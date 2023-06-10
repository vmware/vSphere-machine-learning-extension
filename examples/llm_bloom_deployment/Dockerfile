FROM pytorch/torchserve:latest-gpu

USER root 

ENV NB_USER jovyan
ENV NB_UID 1001
ENV NB_PREFIX /
ENV HOME /home/$NB_USER
ENV SHELL /bin/bash

# create user and set required ownership
RUN useradd -M -s /bin/bash -N -u ${NB_UID} ${NB_USER} \
 && mkdir -p ${HOME} \
 && chown -R ${NB_USER}:users ${HOME} \
 && chown -R ${NB_USER}:users /usr/local/bin

# install git
RUN apt-get update \
&& apt-get install -y --no-install-recommends git

# Install notebook
RUN pip install pip==20.2
RUN pip install ipykernel notebook jupyterlab

# add jupyter path into execute path
ENV PATH="$PATH:~/.local/bin"

EXPOSE 8888

ENV SHELL=/bin/bash
ENV NB_PREFIX /

WORKDIR "${HOME}"

CMD ["exec", "jupyter lab --notebook-dir=/home/jovyan --ip=0.0.0.0 --no-browser --allow-root --port=8888 --NotebookApp.token='' --NotebookApp.password='' --NotebookApp.allow_origin='*' --NotebookApp.base_url=${NB_PREFIX}"]
