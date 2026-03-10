# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.1.0] - 2026-03-10

### Fixed
- `download_and_unzip` with `flatten_directory=True` now performs extraction and
  flattening entirely inside the system temporary directory (short path) before
  moving the result to the final destination.  
  Previously, extraction used a `_tmp` suffix directory placed next to the final
  destination (e.g. `<long_destination>_tmp/<zip_internal_folder>/…`), which
  frequently exceeded the Windows 260-character path limit even when the
  post-flatten paths would have been within the limit.

### Changed
- `download_and_unzip` returns early (via an explicit `return`) when the
  destination already exists, rather than falling through conditionally. This
  makes the skip/resume behaviour more predictable and ensures the flatten step
  is not applied to a pre-existing directory.

### Tests
- Added four offline unit tests (no network required) for `download_and_unzip`
  with `flatten_directory=True`:
  - Verifies flattened content lands at the correct destination.
  - Verifies no `_tmp` directory is left beside the final destination.
  - Verifies non-flatten path behaviour is unchanged.
  - Verifies `subfolder_name` works correctly with flattening.

---

## [1.0.0] - 2026-02-01

### Added
- Initial release.
- `DataDownloader` class with:
  - `download(url, path)` — download with progress indicator; skips if already present.
  - `unzip(zip_file_path, unzip_path, path_test)` — extract ZIP with skip-if-exists guard and Windows path-length check.
  - `download_and_unzip(url, dataset_name, subfolder_name, flatten_directory)` — download + unzip in one call, with optional single-folder flattening.
  - `move_files(patterns, source_directory, destination_directory)` — move file subsets by glob pattern.
  - `download_unzip_keep_subset(url, zip_file_patterns, dataset_name)` — download, unzip, keep only matching files.
