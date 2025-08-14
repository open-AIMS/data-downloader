import os
import zipfile
from pathlib import Path

import pytest

from data_downloader import DataDownloader


def test_download_text_file(tmp_download_dir, gh_base_url):
    dd = DataDownloader(download_path=tmp_download_dir)
    url = f"{gh_base_url}/text.txt"
    dest = os.path.join(tmp_download_dir, "text.txt")
    print(f"DEBUG download URL: {url}")
    print(f"DEBUG destination: {dest}")

    dd.download(url, dest)

    assert os.path.exists(dest)
    with open(dest, "r", encoding="utf-8") as f:
        content = f.read().strip()
    assert "tiny test asset" in content


def test_download_and_unzip_root_zip(tmp_download_dir, gh_base_url):
    dd = DataDownloader(download_path=tmp_download_dir)
    url = f"{gh_base_url}/file-in-root-folder.zip"
    print(f"DEBUG download URL: {url}")

    dd.download_and_unzip(url, dataset_name="root_zip")

    # Expect the files to be extracted directly under download_path/root_zip/
    base = Path(tmp_download_dir) / "root_zip"
    assert (base / "keep.txt").exists()
    assert (base / "drop.csv").exists()


def test_download_and_unzip_nested_zip_flatten(tmp_download_dir, gh_base_url):
    dd = DataDownloader(download_path=tmp_download_dir)
    url = f"{gh_base_url}/file-in-subfolder.zip"
    print(f"DEBUG download URL: {url}")

    # First extract into dataset folder
    dd.download_and_unzip(url, dataset_name="nested_zip")

    base = Path(tmp_download_dir) / "nested_zip"
    # By default, nested folder exists; now call with flatten_directory=True to move content up
    dd.download_and_unzip(url, dataset_name="nested_zip_flat", flatten_directory=True)

    flat_base = Path(tmp_download_dir) / "nested_zip_flat"
    # After flattening, inner.txt should be directly under the target folder
    assert (flat_base / "inner.txt").exists()


def test_download_unzip_keep_subset(tmp_download_dir, gh_base_url):
    dd = DataDownloader(download_path=tmp_download_dir)
    url = f"{gh_base_url}/file-in-root-folder.zip"
    print(f"DEBUG download URL: {url}")

    dd.download_unzip_keep_subset(url, ["*.txt"], dataset_name="subset_zip")

    base = Path(tmp_download_dir) / "subset_zip"
    # Only keep.txt should have been moved
    assert (base / "keep.txt").exists()
    assert not (base / "drop.csv").exists()
