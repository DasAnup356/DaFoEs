#!/usr/bin/env python3
"""Download or set up datasets expected by this repository.

This repo expects datasets to exist at the project root:

- `visu_depth_haptic_data/` (DaFoEs)
- `experiment_data/` (dVRK dataset used in the paper)

For licensing reasons, the datasets are not stored in this repository.
This script helps by downloading an archive from a user-provided URL and
extracting it into the correct folder.
"""

from __future__ import annotations

import argparse
import shutil
import sys
import tarfile
import zipfile
from pathlib import Path
from urllib.parse import urlparse

try:
    from urllib.request import urlretrieve
except ImportError:  # pragma: no cover
    urlretrieve = None


REPO_ROOT = Path(__file__).resolve().parents[1]


def _default_output_dir(dataset: str) -> Path:
    if dataset == "dafoes":
        return REPO_ROOT / "visu_depth_haptic_data"
    if dataset == "dvrk":
        return REPO_ROOT / "experiment_data"
    raise ValueError(f"Unknown dataset: {dataset}")


def _extract(archive_path: Path, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)

    if archive_path.suffix == ".zip":
        with zipfile.ZipFile(archive_path) as zf:
            zf.extractall(dest)
        return

    # Handle .tar, .tar.gz, .tgz
    if archive_path.suffix in {".tar", ".gz"} or archive_path.name.endswith((".tar.gz", ".tgz")):
        with tarfile.open(archive_path, "r:*") as tf:
            tf.extractall(dest)
        return

    raise ValueError(f"Unsupported archive type: {archive_path.name}")


def _download(url: str, out_path: Path) -> None:
    if urlretrieve is None:
        raise RuntimeError("Python environment missing urllib.request")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    urlretrieve(url, out_path)  # nosec - URL is provided by the user intentionally


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Download/extract datasets for DaFoEs")
    parser.add_argument("--dataset", choices=["dafoes", "dvrk"], required=True)
    parser.add_argument(
        "--url",
        help="HTTP(S) URL to a .zip/.tar/.tar.gz/.tgz archive containing the dataset",
    )
    parser.add_argument(
        "--archive",
        type=Path,
        help="Path to a local dataset archive (zip/tar/tar.gz/tgz)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output directory (defaults to repo-expected path)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Delete output directory first if it exists",
    )
    args = parser.parse_args(argv)

    if bool(args.url) == bool(args.archive):
        parser.error("Provide exactly one of --url or --archive")

    dest = args.output if args.output else _default_output_dir(args.dataset)
    if args.force and dest.exists():
        shutil.rmtree(dest)

    if args.url:
        parsed = urlparse(args.url)
        name = Path(parsed.path).name or f"{args.dataset}.archive"
        archive_path = REPO_ROOT / ".cache" / "datasets" / name
        print(f"Downloading {args.url} -> {archive_path}")
        _download(args.url, archive_path)
    else:
        archive_path = args.archive
        if not archive_path.exists():
            raise FileNotFoundError(str(archive_path))

    print(f"Extracting {archive_path} -> {dest}")
    _extract(archive_path, dest)
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

