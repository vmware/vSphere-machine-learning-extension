import argparse
import os

from huggingface_hub import snapshot_download


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--local_dir",
        type=str,
        default="model",
        help="Output directory for downloaded model files",
    )
    parser.add_argument(
        "--model_name", "-m", type=str, required=True, help="HuggingFace model name"
    )
    parser.add_argument("--revision", "-r", type=str, default="main", help="Revision")
    args = parser.parse_args()
    return args


def main():
    if os.path.isdir(args.local_dir):
        if len(os.listdir(args.local_dir)) > 0:
            raise OSError(f"The directory: {args.local_dir} is NOT empty.")
    else:
        os.makedirs(args.local_dir)

    snapshot_path = snapshot_download(
        repo_id=args.model_name,
        revision=args.revision,
        # allow_patterns=allow_patterns,
        # cache_dir=args.model_path,
        local_dir=args.local_dir,
        # token=args.access_token,
    )
    print(f"Files for '{args.model_name}' is downloaded to '{snapshot_path}'")


if __name__ == '__main__':
    args = get_args()

    main()
