# data-downloader

Data-downloader is a tiny, no-dependencies helper that standardises how you pull and arrange external datasets for analysis. It saves everything under a single data root so each dataset lives in its own folder, optionally flattens wrapper folders found inside ZIPs, and provides simple patterns to keep only the files you need. The aim is to make data-fetch scripts reproducible, resumable, and easy to extend without re-downloading what you already have.

Features:
- Download files with a simple progress indicator
- Unzip archives to a target folder (optionally flatten a nested folder)
- Move/copy a subset of files from a larger download

## How to use this library in your project (consumers)

Add this package to your project’s conda environment. If you manage environments with conda, include the following under the pip section of your project’s environment file:

```yaml
name: your-project
channels:
  - conda-forge
dependencies:
  - python>=3.8
  - pip
  - pip:
      - git+https://github.com/open-AIMS/data-downloader@v1.0.0  # pin a tag for reproducibility
```

Alternatively, see `example-environment-consumer.yml` in this repo for a ready-made template.

If you prefer, you can also install directly into an existing environment:

```
pip install "git+https://github.com/open-AIMS/data-downloader@v1.0.0"
```

Note: Replace `v1.0.0` with the tag or commit you want to pin.

## Pin to a tag or commit
To create and push a tag for releases:

```
git tag v1.0.0
git push origin v1.0.0
```

## Supported Python versions
The code uses only the standard library and supports Python 3.8–3.13.

## Quick usage

```python
from data_downloader import DataDownloader

downloader = DataDownloader(download_path="data-cache")
url = "https://example.com/mydata.zip"
downloader.download_and_unzip(url, dataset_name="my_dataset", flatten_directory=True)
```

See `examples/example-download-input-data.py` for a full example script.

## Using the LLM primer with AI assistants
- Open `LLM_PRIMER.md` at the repo root.
- Copy the entire file and paste it into your AI chat at the start of the session to prime the model with this library’s purpose, API, invariants, and patterns.
- Optionally append your project specifics (your `download_path`, dataset and subfolder names, and the URLs you intend to fetch) so generated code matches your layout.
- Re-paste the primer if the chat resets or after you update the library/version.
- Don’t paste secrets or credentials; public dataset URLs are fine.

## Applying DataDownloader in common scenarios

### General pattern and idempotency
- Choose a single data root (e.g., `data/in-3p`). All datasets download underneath this root.
- One dataset → one folder: `data_root/dataset_name`.
- Multi-part datasets → subfolders: `data_root/dataset_name/subfolder_name` for each part.
- Skipping/resume:
  - `download(url, path)` skips if `path` already exists.
  - `download_and_unzip(url, dataset, subfolder=None)` skips if the target folder exists:
    - Without subfolder: skip if `data_root/dataset` exists.
    - With subfolder: skip if `data_root/dataset/subfolder` exists.
  - This lets you re-run and expand scripts without re-downloading. Delete the dataset (or subfolder) folder to force a refresh.

### Scenario 1: Simple ZIP → dataset folder
- When: The ZIP extracts files at the top level (no wrapper folder).
- Example:
  ```python
  downloader.download_and_unzip("https://.../ne_10m_land.zip", "ne_10m_land")
  ```
- Result: `data/in-3p/ne_10m_land/*`

### Scenario 2: ZIP has a single wrapper folder → flatten
- When: The provider wraps files in one top-level folder you don’t need (common with some Nextcloud links).
- Example:
  ```python
  downloader.download_and_unzip(nextcloud_url,
                                "AU_AIMS_Coastline_50k_2024",
                                subfolder_name="Split",
                                flatten_directory=True)
  ```
- Behavior:
  - If exactly one top-level directory exists after extraction, its contents are moved up.
  - If multiple top-level directories are found, a WARNING is printed and flattening is skipped.

### Scenario 3: One dataset, multiple parts → subfolders (+ optional flatten)
- When: You want related variants side-by-side (e.g., `Split` and `Simp`).
- Example:
  ```python
  downloader.download_and_unzip(url_split, "AU_AIMS_Coastline_50k_2024", subfolder_name="Split", flatten_directory=True)
  downloader.download_and_unzip(url_simp,  "AU_AIMS_Coastline_50k_2024", subfolder_name="Simp",  flatten_directory=True)
  ```
- Why: `subfolder_name` prevents skipping when the parent dataset folder already exists.

### Scenario 4: Download a single file (no unzip)
- When: Direct assets like GeoPackage/CSV/NetCDF.
- Example:
  ```python
  dest = os.path.join(downloader.download_path, "AU_ICSM_Gazetteer_2018.gpkg")
  downloader.download("https://.../PlaceNames.gpkg", dest)
  ```

### Scenario 5: ZIP contains nested ZIPs or mixed files → add a small post-step
- When: Bundles like EOT20 include `ocean_tides.zip` and `load_tides.zip` inside the main ZIP.
- Pattern:
  ```python
  downloader.download_and_unzip(eot20_url, "World_EOT20_2021")
  # Manually unzip only ocean_tides.zip; optionally delete load_tides.zip to save space.
  ```
- Note: The downloader doesn’t automatically extract nested archives.

### Organizing your data (one possible convention)
- A practical split is:
  - `data/in-3p` for third‑party inputs (eAtlas/GA/Natural Earth/etc.).
  - `data/in` for project‑specific inputs used in your processing.
- You can switch mid‑script if needed:
  ```python
  downloader.download_path = "data/in"
  ```
- This is just one way to organise data. Use what fits your project and publishing workflow.

### Flattening behavior and warnings
- `flatten_directory` only acts when there’s exactly one top-level directory after extraction.
- If multiple top-level directories are present, a WARNING is printed and flattening is skipped (often indicates an unexpected package layout).
- Tip: To decide whether to flatten, first download with a browser and inspect the ZIP’s internal structure.

### When to use something else
- Resume granularity: This library resumes at the dataset/subfolder level, not mid‑file.
  - For very large single files where partial‑file resume is critical, consider `curl`/`wget`/`aria2c` or storage SDKs (e.g., `boto3`).
  - Note: downloads of ~60 GB single files have worked, but there’s no mid‑transfer resume if interrupted.
- Authenticated or API‑driven sources (e.g., signed URLs, WFS/WCS): use appropriate SDKs/clients (e.g., `boto3`, `requests`, GIS libs).
- Complex post‑processing (reprojection, format conversion, .prj fixes): use GDAL/pyproj or GIS tooling.
- Multi‑stage or deeply nested archives beyond simple flattening: add bespoke steps around this library.

### Practical tips
- Be deliberate with `dataset_name` and `subfolder_name` to keep folders clean and enable correct skip/resume.
- Use `flatten_directory=True` when you know there’s a single wrapper folder (common with Nextcloud folder downloads).
- For reproducibility, pin stable URLs/tags and record citations/DOIs in comments next to downloads.
- If you only need a subset of files from a big ZIP, prefer the subset flow to save disk space.
- Windows path length: unzip checks for >260 chars and will error; shorten the data root or folder names if needed.

## License
MIT. See `LICENSE`.

## Developing this library (contributors)

Create a local development environment that installs this package in editable mode:

See `example-environment-dev.yml` and run:

```
conda env create -f example-environment-dev.yml
conda activate data-downloader-dev
```

#### Why a dev environment and `-e .`?
- `-e .` means “editable install” (i.e., `pip install -e .`). It installs the package by linking to your local source so changes under `src/data_downloader/` are picked up immediately without reinstalling.
- Installing the package (editable or not) ensures `import data_downloader` works in tests and examples, because Python sees it as an installed distribution. Without installing, imports may fail unless you tweak `PYTHONPATH`.
- A dedicated conda env is convenient but not strictly required. You may use any existing environment that meets requirements (Python 3.8+). Simply run:
  - `pip install -e .`
  - `pip install pytest`
  Then run `pytest -q` from the repo root.
- Consumers should not use `-e .`; they install from a Git tag via `pip install "git+https://github.com/open-AIMS/data-downloader@<tag>"`.


### Running tests

Tests use pytest and download tiny public assets from this repo via GitHub raw URLs.

1) Install pytest (if not already):
   - `conda install pytest` or `pip install pytest`
2) Assets: small files live in `tests/assets/` and are referenced via raw URLs.
   - If you change assets, regenerate the zip files locally: `python tests/assets/generate_test_zips.py` and commit the results.
3) Before a tag exists, point tests at your branch/commit by setting `GH_ASSETS_BASE_URL` to a raw URL, for example:
   - Anaconda Prompt (Windows cmd):
     - `set GH_ASSETS_BASE_URL=https://raw.githubusercontent.com/open-AIMS/data-downloader/refs/heads/main/tests/assets`
   - Bash (Windows Git Bash):
     - `export GH_ASSETS_BASE_URL=https://raw.githubusercontent.com/open-AIMS/data-downloader/<branch-or-commit>/tests/assets`
   - PowerShell:
     - `$env:GH_ASSETS_BASE_URL = "https://raw.githubusercontent.com/open-AIMS/data-downloader/<branch-or-commit>/tests/assets"`
   - After tagging (e.g., v1.0.1), no env var is needed because tests default to `.../v1.0.1/tests/assets` once you update the placeholder.
   - For the lastest version use `<branch-or-commit>` as `refs/heads/main`
4) Run tests:
   - `pytest -q`

Notes:
- Tests rely on network access to GitHub and may be slower/flaky offline.
- Assertions check that downloaded files land in the right location and expected names/contents exist.

### Releasing and tagging

What does `@v1.0.0` mean?
- It refers to a Git tag named `v1.0.0` on this repository. Consumers pin to that tag to get a reproducible version.

Steps to cut a new release (SemVer: MAJOR.MINOR.PATCH):
1) Choose the new version (e.g., 1.0.1) and update it in both places:
   - `pyproject.toml`: `[project].version`
   - `src/data_downloader/__init__.py`: `__version__`
2) Commit the changes on the default branch (e.g., main):
   - `git add pyproject.toml src/data_downloader/__init__.py`
   - `git commit -m "Bump version to 1.0.1"`
3) Create an annotated tag and push it:
   - `git tag -a v1.0.1 -m "Release v1.0.1"`
   - `git push origin main`
   - `git push origin v1.0.1`
4) Consumers can now install this exact version:
   - `pip install "git+https://github.com/open-AIMS/data-downloader@v1.0.1"`
   - Or include the same line under `pip:` in their `environment.yml`.
5) Optional: Create a GitHub Release for `v1.0.1` in the web UI and add release notes.

Fixing a mistaken tag (if needed):
- Delete local tag: `git tag -d v1.0.1`
- Delete remote tag: `git push origin :refs/tags/v1.0.1`
- Recreate and push the corrected tag.