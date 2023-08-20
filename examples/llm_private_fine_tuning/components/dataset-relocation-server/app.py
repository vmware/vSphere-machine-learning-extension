import argparse
import shutil

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset_destination_path', type=str, help='dataset destination path')

    opt = parser.parse_args()
    dataset_destination_path = opt.dataset_destination_path
    print("Relocating to: " + dataset_destination_path)
    shutil.copytree("./datasets", dataset_destination_path, dirs_exist_ok=True)
