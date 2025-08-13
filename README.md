# data-downloader

This package is intended to make downloading datasets for data analysis easier.

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
   - Bash (Windows Git Bash):
     - `export GH_ASSETS_BASE_URL="https://raw.githubusercontent.com/open-AIMS/data-downloader/<branch-or-commit>/tests/assets"`
   - PowerShell:
     - `$env:GH_ASSETS_BASE_URL = "https://raw.githubusercontent.com/open-AIMS/data-downloader/<branch-or-commit>/tests/assets"`
   - After tagging (e.g., v1.0.1), no env var is needed because tests default to `.../v1.0.1/tests/assets` once you update the placeholder.
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