# Carvel Package: Kubeflow
---

### Prerequisites

- Carvel Tools: https://carvel.dev/ytt/docs/v0.43.0/install/#via-script-macos-or-linux (please use 'Via script' methods)
- Docker: https://docs.docker.com/engine/install/
- Kustomize v3.2.0: https://github.com/kubernetes-sigs/kustomize/releases/tag/v3.2.0

### Directory Structure

```bash
├── README.md
├── bundle                      # The Kubeflow Carvel Package Manifest
│   ├── config
│   │   ├── overlays            # Carvel ytt Overlays
│   │   ├── psp.yaml 
│   │   ├── upstream            # Kubeflow upstream manifests
│   │   ├── values-schema.yaml 
│   │   └── values.yaml  
│   ├── vendir.lock.yml
│   └── vendir.yml
├── download_upstream.sh        # scripts to download Kubeflow upstream manifests
├── repo                        # The Kubeflow Carvel PackageRepository Manifest
│   └── packages
│       ├── 1.6.0.yml
│       └── metadata.yaml
└── update_packages.sh          # scripts to update new Kubeflow Carvel Package / PackageRepository
```

### Getting started

Download Kubeflow upstream manifests
```bash
./download_upstream.sh
```

Update Kubeflow Carvel Package / PackageRepository
```bash
./update_packages.sh
```