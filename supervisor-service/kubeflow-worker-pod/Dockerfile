FROM ubuntu:20.04
WORKDIR /app
RUN apt update && \
    apt install -y curl jq libdigest-sha-perl unzip && \
    apt clean

ENV http_proxy http://proxy.vmware.com:3128
ENV HTTP_PROXY http://proxy.vmware.com:3128
ENV https_proxy http://proxy.vmware.com:3128
ENV HTTPS_PROXY http://proxy.vmware.com:3128

RUN curl https://carvel.dev/install.sh --output carvel_install.sh && \
    bash carvel_install.sh && \
    rm carvel_install.sh
COPY . ./
