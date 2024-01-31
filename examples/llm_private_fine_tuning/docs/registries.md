## Using other registries

### External GitHub

```bash
export GH_ACCESS_TOKEN=""
echo $GH_ACCESS_TOKEN | docker login ghcr.io -u albertoimpl --password-stdin
```

```bash
export NEXT_VERSION="v1.0.55"

docker build -t model-relocation-server ./components/model-relocation-server
docker tag "model-relocation-server" "ghcr.io/albertoimpl/model-relocation-server:${NEXT_VERSION}"
docker push "ghcr.io/albertoimpl/model-relocation-server:${NEXT_VERSION}"

docker build -t tokenizer-relocation-server ./components/tokenizer-relocation-server
docker tag "tokenizer-relocation-server" "ghcr.io/albertoimpl/tokenizer-relocation-server:${NEXT_VERSION}"
docker push "ghcr.io/albertoimpl/tokenizer-relocation-server:${NEXT_VERSION}"

docker build -t model-reference-relocation-server ./components/model-reference-relocation-server
docker tag "model-reference-relocation-server" "ghcr.io/albertoimpl/model-reference-relocation-server:${NEXT_VERSION}"
docker push "ghcr.io/albertoimpl/model-reference-relocation-server:${NEXT_VERSION}"

docker build -t dataset-relocation-server ./components/dataset-relocation-server
docker tag "dataset-relocation-server" "ghcr.io/albertoimpl/dataset-relocation-server:${NEXT_VERSION}"
docker push "ghcr.io/albertoimpl/dataset-relocation-server:${NEXT_VERSION}"

docker build -t model-inference-server ./components/model-inference-server
docker tag "model-inference-server" "ghcr.io/albertoimpl/model-inference-server:${NEXT_VERSION}"
docker push "ghcr.io/albertoimpl/model-inference-server:${NEXT_VERSION}"

docker build -t model-peft-server ./components/model-peft-server
docker tag "model-peft-server" "ghcr.io/albertoimpl/model-peft-server:${NEXT_VERSION}"
docker push "ghcr.io/albertoimpl/model-peft-server:${NEXT_VERSION}"

docker build -t model-evaluation-server ./components/model-evaluation-server
docker tag "model-evaluation-server" "ghcr.io/albertoimpl/model-evaluation-server:${NEXT_VERSION}"
docker push "ghcr.io/albertoimpl/model-evaluation-server:${NEXT_VERSION}"

docker build -t model-inference-server ./components/model-inference-server
docker tag "model-inference-server" "ghcr.io/albertoimpl/model-inference-server:${NEXT_VERSION}"
docker push "ghcr.io/albertoimpl/model-inference-server:${NEXT_VERSION}"
```

### Local KinD

Images can be preloaded in KinD to speed the process up.

```bash
export NEXT_VERSION="v1.0.55"

docker build -t model-relocation-server ./components/model-relocation-server
docker tag "model-relocation-server" "ghcr.io/albertoimpl/model-relocation-server:${NEXT_VERSION}"
kind load docker-image "ghcr.io/albertoimpl/model-relocation-server:${NEXT_VERSION}"

docker build -t tokenizer-relocation-server ./components/tokenizer-relocation-server
docker tag "tokenizer-relocation-server" "ghcr.io/albertoimpl/tokenizer-relocation-server:${NEXT_VERSION}"
kind load docker-image "ghcr.io/albertoimpl/tokenizer-relocation-server:${NEXT_VERSION}"

docker build -t model-reference-relocation-server ./components/model-reference-relocation-server
docker tag "model-reference-relocation-server" "ghcr.io/albertoimpl/model-reference-relocation-server:${NEXT_VERSION}"
kind load docker-image "ghcr.io/albertoimpl/model-reference-relocation-server:${NEXT_VERSION}"

docker build -t dataset-relocation-server ./components/dataset-relocation-server
docker tag "dataset-relocation-server" "ghcr.io/albertoimpl/dataset-relocation-server:${NEXT_VERSION}"
kind load docker-image "ghcr.io/albertoimpl/dataset-relocation-server:${NEXT_VERSION}"

docker build -t model-inference-server ./components/model-inference-server
docker tag "model-inference-server" "ghcr.io/albertoimpl/model-inference-server:${NEXT_VERSION}"
kind load docker-image "ghcr.io/albertoimpl/model-inference-server:${NEXT_VERSION}"

docker build -t model-peft-server ./components/model-peft-server
docker tag "model-peft-server" "ghcr.io/albertoimpl/model-peft-server:${NEXT_VERSION}"
kind load docker-image "ghcr.io/albertoimpl/model-peft-server:${NEXT_VERSION}"

docker build -t model-evaluation-server ./components/model-evaluation-server
docker tag "model-evaluation-server" "ghcr.io/albertoimpl/model-evaluation-server:${NEXT_VERSION}"
kind load docker-image "ghcr.io/albertoimpl/model-evaluation-server:${NEXT_VERSION}"

docker build -t model-inference-server ./components/model-inference-server
docker tag "model-inference-server" "ghcr.io/albertoimpl/model-inference-server:${NEXT_VERSION}"
kind load docker-image "ghcr.io/albertoimpl/model-inference-server:${NEXT_VERSION}"
```

```bash
skaffold run --tag=${NEXT_VERSION}
```

### External Harbor Registry

Using Harbor demo environment. After creating an account in `demo.goharbor.io` and creating a project:

```bash
export REGISTRY_PROJECT_NAME=alberto-test

docker login demo.goharbor.io -u rcallejarios -p ${DEMO_ACCOUNT_PASSWORD}

docker build -t model-relocation-server ./components/model-relocation-server
docker tag "model-relocation-server" "demo.goharbor.io/${REGISTRY_PROJECT_NAME}/model-relocation-server"
docker push "demo.goharbor.io/${REGISTRY_PROJECT_NAME}/model-relocation-server"
```
