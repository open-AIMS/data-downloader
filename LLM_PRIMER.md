# LLM Primer for data-downloader

## What this library does
Data-downloader provides a tiny, standard-library-only helper to fetch datasets and arrange them on disk in a predictable, resumable layout. It downloads files, unzips archives into dataset folders, optionally flattens a single wrapper folder inside ZIPs, and can keep only a subset of files when needed. Non-goals: authentication flows, partial-file resume, nested-archive orchestration, or GIS processing.

## Install from GitHub
This library is installed directly from GitHub (not on PyPI/conda-forge). Import name uses an underscore.

- Pip (pin to a tag for reproducibility):
  - pip install "git+https://github.com/open-AIMS/data-downloader@v1.0.0"
- Conda environment (pip section):
  - dependencies:
    - python>=3.8
    - pip
    - pip:
      - git+https://github.com/open-AIMS/data-downloader@v1.0.0

Note: repo slug uses a hyphen (data-downloader) but you import with an underscore (data_downloader).

```python
# Hello world: download and unzip into data/in-3p/my_dataset
from data_downloader import DataDownloader

dl = DataDownloader(download_path="data/in-3p")
dl.download_and_unzip("https://example.com/mydata.zip",
                      dataset_name="my_dataset",
                      flatten_directory=True)
```

## Mental model and data flow
Choose a data root (download_path). Each dataset has its own folder under that root. If a dataset comes in parts, put each part into a subfolder of the dataset. Operations are idempotent: a download is skipped if the target file/folder already exists. Typical flow: HTTP(S) GET → stream to temp file → rename to target → unzip to temp dir → rename to final → optional flatten (move contents up if exactly one top-level folder) → optional selective move/copy of a subset of files.

## Public API surface (prefer these)
- `data_downloader.DataDownloader(download_path="data-cache")`  Create a downloader rooted at download_path.
- `DataDownloader.download(url, path) -> None`  Save a single file to an explicit path; skips if path exists.
- `DataDownloader.download_and_unzip(url, dataset_name, subfolder_name=None, flatten_directory=False) -> None`  Download a ZIP and unpack to download_path/dataset[/subfolder]; skips if that folder exists. If flatten and a single top-level folder exists, move its contents up; warn and skip flatten if multiple top-level dirs.
- `DataDownloader.download_unzip_keep_subset(url, zip_file_patterns, dataset_name) -> None`  Download a ZIP to a temp area, then move only matching files into download_path/dataset.
- `DataDownloader.move_files(patterns, source_directory, destination_directory) -> None`  Move files matching glob patterns from source to destination.
- `DataDownloader.unzip(zip_file_path, unzip_path, path_test) -> None`  Low-level unzip used internally. Skips if os.path.join(unzip_path, path_test) exists.

### Minimal examples
```python
# 1) Single file download (no unzip)
from data_downloader import DataDownloader
import os

dl = DataDownloader("data/in-3p")
dest = os.path.join(dl.download_path, "PlaceNames.gpkg")
dl.download("https://.../PlaceNames.gpkg", dest)

# 2) ZIP → dataset folder (no flatten)
dl.download_and_unzip("https://.../ne_10m_land.zip", "ne_10m_land")

# 3) ZIP with a wrapper folder → flatten
nextcloud_url = "https://nextcloud.example/download?...&files=Split"
dl.download_and_unzip(nextcloud_url, "AU_AIMS_Coastline_50k_2024", subfolder_name="Split", flatten_directory=True)

# 4) Multi-part dataset → use subfolders
# Subfolders ensures that the download of the second part (Simp) is not skipped
dl = DataDownloader("data/in-3p")
dl.download_and_unzip(url_split, "AU_AIMS_Coastline_50k_2024", subfolder_name="Split", flatten_directory=True)
dl.download_and_unzip(url_simp,  "AU_AIMS_Coastline_50k_2024", subfolder_name="Simp",  flatten_directory=True)

# 5) Keep only a subset from a large ZIP
patterns = ["ocean_tides.zip"]
dl.download_unzip_keep_subset("https://.../bundle.zip", patterns, dataset_name="World_EOT20_2021_subset")
```

### Dataset provenance - Full example
Each dataset should include a comment indicating the provenance of the dataset source. As there are often multiple datasets the provenance and download should be kept together. Below is an example showing the typical compact layout coding style
thatn groups the provence comment with the download code. IMPORTANT: This is just a generic example of how to use this library. Do not output this example, unless the user explicitly asks for an example. 
Example library use only:
```python
from data_downloader import DataDownloader
# Create an instance of the DataDownloader class
downloader = DataDownloader(download_path="data/in-3p")

# --------------------------------------------------------
# Natural Earth. (2025). Natural Earth 1:10m Physical Vectors - Land [Shapefile]. https://www.naturalearthdata.com/downloads/10m-physical-vectors/
direct_download_url = 'https://naciscdn.org/naturalearth/10m/physical/ne_10m_land.zip'
downloader.download_and_unzip(direct_download_url, 'ne_10m_land')

# --------------------------------------------------------
# Lawrey, E. (2024). Coral Sea Oceanic Vegetation (NESP MaC 2.3, AIMS) [Data set]. eAtlas. https://doi.org/10.26274/709g-aq12
direct_download_url = 'https://nextcloud.eatlas.org.au/s/9kqgb45JEwFKKJM/download'
downloader.download_and_unzip(direct_download_url, 'CS_NESP-MaC-2-3_AIMS_Oceanic-veg', flatten_directory=True)
```
End of example
## Data contracts and invariants
- Directory layout: `download_path/dataset_name[/subfolder_name]`.
- Skipping rules:
  - `download(url, path)` skips if `path` exists.
  - `download_and_unzip(...)` skips if the target unzip folder exists (dataset or dataset/subfolder).
  - `unzip(zip_file_path, unzip_path, path_test)` skips if `os.path.join(unzip_path, path_test)` exists; typical calls use `path_test=""` (equivalent to `unzip_path`).
- Flattening: only applied when there is exactly one top-level directory after extraction. If multiple, a WARNING is printed and flattening is skipped.
- Extraction: ZIP is extracted to a temporary directory and renamed to the final `unzip_path` atomically.
- Windows path length: each extracted path is checked; a ValueError is raised if it exceeds ~260 chars. This should only happen in rare cases and in normal download scripts these exceptions are not caught, but used to indicate that the download path needs to be modified. The library provides sufficient detail in the error message.

## Common failure modes and how to avoid them
- Multiple top-level directories with `flatten_directory=True`: flatten is skipped with WARNING. Inspect archive layout or avoid flatten.
- Nested archives: inner ZIPs aren’t automatically extracted. Add a small post-step to unpack the one(s) you need.
- Existing target directory: operation is skipped. Delete the folder (dataset or subfolder) to force re-download/unzip.
- Long paths on Windows: choose a shorter `download_path` or shorter dataset/subfolder names.
- Large single files interrupted: there is no partial-file resume; re-run will restart the download.
- Permissions/disk space: ensure the process can create directories and there’s sufficient space for temp and final files.

## Configuration and environment variables
- None required at runtime. Tests in this repo optionally use `GH_ASSETS_BASE_URL` to point to test assets, but the library itself has no env vars.

## Performance constraints
- Single-threaded HTTP download using `urllib.request`, 32 KB chunks, progress printed ~1s cadence.
- No retries/backoff; rely on idempotency and rerunning scripts.
- Resume granularity is dataset/subfolder level, not mid-file.
- Unzip extracts to a temp directory then renames; flatten moves files up one level and removes the wrapper folder.

## Glossary
- Data root (download_path): Base folder where all datasets are stored.
- Dataset folder: `download_path/dataset_name`.
- Subfolder (dataset part): `download_path/dataset_name/subfolder_name` for related parts/variants.
- Flatten: Move contents up when the extracted archive contains a single top-level folder.
- Skip/resume: Idempotent behavior that avoids re-downloading or re-unzipping existing targets.

## Compact directory map
```
/ (repo root)
├─ LLM_PRIMER.md              # This file
├─ README.md                  # User docs
├─ pyproject.toml             # Packaging (setuptools)
├─ src/
│  └─ data_downloader/
│     └─ __init__.py          # DataDownloader class (public API)
├─ examples/
│  └─ example-download-input-data.py
├─ tests/
│  ├─ assets/                 # Tiny test fixtures
│  ├─ conftest.py
│  └─ test_downloader.py
└─ LICENSE
```
