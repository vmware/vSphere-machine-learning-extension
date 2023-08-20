import kfp.dsl as dsl

VERSION = "v1.0.55"


def create_models_volume():
    return dsl.VolumeOp(name="base-model-pvc",
                        resource_name="base-model-pvc",
                        size='30Gi',
                        modes=dsl.VOLUME_MODE_RWO)


def create_reference_models_volume():
    return dsl.VolumeOp(name="reference-model-pvc",
                        resource_name="reference-model-pvc",
                        size='30Gi',
                        modes=dsl.VOLUME_MODE_RWO)


def create_datasets_volume():
    return dsl.VolumeOp(name="datasets-pvc",
                        resource_name="datasets-pvc",
                        size='5Gi',
                        modes=dsl.VOLUME_MODE_RWO)


def create_tokenizers_volume():
    return dsl.VolumeOp(name="base-tokenizer-pvc",
                        resource_name="base-tokenizer-pvc",
                        size='5Gi',
                        modes=dsl.VOLUME_MODE_RWO)


def create_fine_tuned_volume():
    return dsl.VolumeOp(name="fine-tuned-model-pvc",
                        resource_name="fine-tuned-model-pvc",
                        size='30Gi',
                        modes=dsl.VOLUME_MODE_RWO)


def relocate_dataset(datasets_volume):
    return dsl.ContainerOp(
        name='Relocate dataset',
        image='ghcr.io/albertoimpl/dataset-relocation-server:' + VERSION,
        pvolumes={
            '/datasets': datasets_volume.volume
        },
        command=['python3', 'app.py'],
        arguments=[
            "--dataset_destination_path", "/datasets"
        ],
    )


def relocate_model(models_volume):
    return dsl.ContainerOp(
        name='Relocate model',
        image='ghcr.io/albertoimpl/model-relocation-server:' + VERSION,
        pvolumes={
            '/base-model': models_volume.volume
        },
        command=['python3', 'app.py'],
        arguments=[
            "--model_destination_path", "/base-model/model"
        ],
    )


def relocate_tokenizer(tokenizers_volume):
    return dsl.ContainerOp(
        name='Relocate tokenizer',
        image='ghcr.io/albertoimpl/tokenizer-relocation-server:' + VERSION,
        pvolumes={
            '/base-tokenizer': tokenizers_volume.volume
        },
        command=['python3', 'app.py'],
        arguments=[
            "--tokenizer_destination_path", "/base-tokenizer/tokenizer"
        ],
    )


def relocate_reference_model(reference_model_volume):
    return dsl.ContainerOp(
        name='Relocate reference model',
        image='ghcr.io/albertoimpl/model-reference-relocation-server:' + VERSION,
        pvolumes={
            '/reference-model': reference_model_volume.volume
        },
        command=['python3', 'app.py'],
        arguments=[
            "--model_destination_path",
            "/reference-model/models",
            "--tokenizer_destination_path",
            "/reference-model/tokenizers"
        ],
    )


def fine_tune_model_with_dataset(base_model, base_tokenizer, dataset, finetuned_model_volume, epochs):
    return dsl.ContainerOp(
        name='Fine-tune model with dataset',
        image='ghcr.io/albertoimpl/model-peft-server:' + VERSION,
        pvolumes={
            '/base-model': base_model.pvolumes['/base-model'],
            '/base-tokenizer': base_tokenizer.pvolumes['/base-tokenizer'],
            '/datasets': dataset.pvolumes['/datasets'],
            '/fine-tuned-model': finetuned_model_volume.volume,
        },
        command=['python3', 'app.py'],
        arguments=[
            '--epochs', epochs,
            "--base_model_full_path", "/base-model/model/gpt2",
            "--dataset_full_path", "/datasets/dataset.csv",
            "--base_tokenizer_full_path", "/base-tokenizer/tokenizer/gpt2",
            "--fine_tuned_model_full_path", "/fine-tuned-model/model/gpt2",
        ],
    ).set_gpu_limit(1)


def evaluate_model(base_model, base_tokenizer, reference_model_volume, finetuned_model_volume, proxy_url):
    return dsl.ContainerOp(
        name='Evaluate model capabilities',
        image='ghcr.io/albertoimpl/model-evaluation-server:' + VERSION,
        pvolumes={
            '/base-model': base_model.pvolumes['/base-model'],
            '/base-tokenizer': base_tokenizer.pvolumes['/base-tokenizer'],
            '/reference-model': reference_model_volume.pvolumes['/reference-model'],
            '/fine-tuned-model': finetuned_model_volume.pvolumes['/fine-tuned-model'],
        },
        command=['python3', 'app.py'],
        arguments=[
            "--base_model_full_path", "/base-model/model/gpt2",
            "--base_tokenizer_full_path", "/base-tokenizer/tokenizer/gpt2",
            "--reference_model_full_path", "/reference-model/models/gpt2-large",
            "--reference_tokenizer_full_path", "/reference-model/tokenizers/gpt2-large",
            "--fine_tuned_model_full_path", "/fine-tuned-model/model/gpt2",
            "--proxy_url", proxy_url,
        ],
    ).set_gpu_limit(1)


@dsl.pipeline(
    name='peft-eval-pipeline',
    description='pipeline to fine-tune an llm')
def generate_pipeline(epochs: str = '0.001', proxy_url: str = None):
    datasets_volume = create_datasets_volume()
    models_volume = create_models_volume()
    tokenizers_volume = create_tokenizers_volume()

    finetuned_model_volume = create_fine_tuned_volume()
    reference_model_volume = create_reference_models_volume()

    relocated_model = relocate_model(models_volume)
    relocated_tokenizer = relocate_tokenizer(tokenizers_volume)
    relocated_dataset = relocate_dataset(datasets_volume)
    relocated_reference_model = relocate_reference_model(reference_model_volume)

    fine_tuned_model = fine_tune_model_with_dataset(relocated_model,
                                                    relocated_tokenizer,
                                                    relocated_dataset,
                                                    finetuned_model_volume,
                                                    epochs)

    evaluate_model(relocated_model,
                   relocated_tokenizer,
                   relocated_reference_model,
                   fine_tuned_model,
                   proxy_url)
