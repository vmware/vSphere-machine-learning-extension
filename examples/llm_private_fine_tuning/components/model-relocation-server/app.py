import argparse
import shutil

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_destination_path', type=str, help='model destination path')

    opt = parser.parse_args()
    model_destination_path = opt.model_destination_path
    print("Relocating to: " + model_destination_path)
    shutil.copytree("./models/", model_destination_path, dirs_exist_ok=True)
