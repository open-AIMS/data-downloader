import zipfile
from pathlib import Path

ASSETS_DIR = Path(__file__).parent

# file-in-root-folder.zip: contains keep.txt and drop.csv at root
root_zip = ASSETS_DIR / "file-in-root-folder.zip"
with zipfile.ZipFile(root_zip, "w", compression=zipfile.ZIP_DEFLATED) as z:
    z.writestr("keep.txt", "keep me\n")
    z.writestr("drop.csv", "id,val\n1,2\n")

# file-in-subfolder.zip: contains subfolder/inner.txt
nested_zip = ASSETS_DIR / "file-in-subfolder.zip"
with zipfile.ZipFile(nested_zip, "w", compression=zipfile.ZIP_DEFLATED) as z:
    z.writestr("subfolder/inner.txt", "nested file\n")

print("Generated test zip assets in", ASSETS_DIR)
