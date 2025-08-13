import os
import shutil
import tempfile
import pytest

@pytest.fixture()
def tmp_download_dir(tmp_path):
    # Dedicated per-test download folder
    d = tmp_path / "downloads"
    d.mkdir(parents=True, exist_ok=True)
    yield str(d)

@pytest.fixture()
def gh_base_url():
    """GitHub raw base URL for test assets.
    Override via GH_ASSETS_BASE_URL to test before a tag exists.
    Default points to a tag placeholder; update after tagging.
    """
    return os.environ.get(
        "GH_ASSETS_BASE_URL",
        "https://raw.githubusercontent.com/open-AIMS/data-downloader/v1.0.0/tests/assets",
    )
