import argparse
import shutil

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_destination_path', type=str, help='reference model destination path')
    parser.add_argument('--tokenizer_destination_path', type=str, help='reference tokenizer destination path')

    opt = parser.parse_args()
    model_destination_path = opt.model_destination_path
    print("Relocating model to: " + model_destination_path)
    shutil.copytree("./models", model_destination_path, dirs_exist_ok=True)

    tokenizer_destination_path = opt.tokenizer_destination_path
    print("Relocating tokenizer to: " + tokenizer_destination_path)
    shutil.copytree("./tokenizers", tokenizer_destination_path, dirs_exist_ok=True)
