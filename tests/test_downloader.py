import os
import zipfile
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch

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


# ---------------------------------------------------------------------------
# Offline tests (no network) – verify flatten uses short temp paths
# ---------------------------------------------------------------------------

def _make_nested_zip(zip_path: str, inner_folder: str, filenames: list[str]) -> None:
    """Helper: create a ZIP with files inside a single inner folder."""
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for name in filenames:
            z.writestr(f"{inner_folder}/{name}", f"content of {name}\n")


def test_flatten_extracts_via_short_temp_path(tmp_path):
    """Flattening should extract in system temp (short path), not beside the
    final destination, avoiding Windows 260-char path issues."""
    download_dir = str(tmp_path / "downloads")
    dd = DataDownloader(download_path=download_dir)

    # Create a ZIP with a nested folder
    zip_path = str(tmp_path / "test.zip")
    _make_nested_zip(zip_path, "deep-inner-folder", ["a.txt", "b.csv"])

    # Patch download() so it just copies our local ZIP instead of hitting the network
    def fake_download(self_inner, url, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        shutil.copy2(zip_path, path)

    with patch.object(DataDownloader, "download", fake_download):
        dd.download_and_unzip(
            url="http://fake/test.zip",
            dataset_name="ds",
            flatten_directory=True,
        )

    dest = Path(download_dir) / "ds"
    # Files should be flattened – no deep-inner-folder in the way
    assert (dest / "a.txt").exists()
    assert (dest / "b.csv").exists()
    assert not (dest / "deep-inner-folder").exists()


def test_flatten_no_extract_beside_destination(tmp_path):
    """Ensure no _tmp directory is created next to the final destination
    when flatten_directory=True (all temp work should be in system temp)."""
    download_dir = str(tmp_path / "downloads")
    dd = DataDownloader(download_path=download_dir)

    zip_path = str(tmp_path / "test.zip")
    _make_nested_zip(zip_path, "inner", ["file.txt"])

    def fake_download(self_inner, url, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        shutil.copy2(zip_path, path)

    with patch.object(DataDownloader, "download", fake_download):
        dd.download_and_unzip(
            url="http://fake/test.zip",
            dataset_name="mydata",
            flatten_directory=True,
        )

    dest = Path(download_dir) / "mydata"
    assert (dest / "file.txt").exists()

    # No leftover _tmp directory beside the destination
    assert not (Path(download_dir) / "mydata_tmp").exists()


def test_no_flatten_still_uses_original_path(tmp_path):
    """Without flatten_directory, behaviour should be unchanged – extract
    goes to the final destination via the _tmp rename pattern."""
    download_dir = str(tmp_path / "downloads")
    dd = DataDownloader(download_path=download_dir)

    zip_path = str(tmp_path / "test.zip")
    with zipfile.ZipFile(zip_path, "w") as z:
        z.writestr("root-file.txt", "hello\n")

    def fake_download(self_inner, url, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        shutil.copy2(zip_path, path)

    with patch.object(DataDownloader, "download", fake_download):
        dd.download_and_unzip(
            url="http://fake/test.zip",
            dataset_name="simple",
            flatten_directory=False,
        )

    dest = Path(download_dir) / "simple"
    assert (dest / "root-file.txt").exists()


def test_flatten_with_subfolder(tmp_path):
    """flatten_directory should work correctly with subfolder_name."""
    download_dir = str(tmp_path / "downloads")
    dd = DataDownloader(download_path=download_dir)

    zip_path = str(tmp_path / "test.zip")
    _make_nested_zip(zip_path, "wrapper", ["data.txt"])

    def fake_download(self_inner, url, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        shutil.copy2(zip_path, path)

    with patch.object(DataDownloader, "download", fake_download):
        dd.download_and_unzip(
            url="http://fake/test.zip",
            dataset_name="ds",
            subfolder_name="v1",
            flatten_directory=True,
        )

    dest = Path(download_dir) / "ds" / "v1"
    assert (dest / "data.txt").exists()
    assert not (dest / "wrapper").exists()
