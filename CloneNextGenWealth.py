#!/usr/bin/env python3
"""Create a clone of NextGenWealth with namespace substitutions."""

import argparse
import os
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path


def replace_in_file(file_path: Path, old: str, new: str) -> None:
    """Replace occurrences of `old` with `new` in a file, skipping binary files."""
    try:
        with open(file_path, "rb") as f:
            raw = f.read()
    except OSError:
        return

    if b"\x00" in raw:
        return

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return

    if old not in text:
        return

    new_text = text.replace(old, new)
    with open(file_path, "wb") as f:
        f.write(new_text.encode("utf-8"))


def zip_directory_contents(source_dir: Path, zip_path: Path) -> None:
    """Zip the contents of `source_dir` such that entries are at the top level of the archive."""
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _dirs, files in os.walk(source_dir):
            root_path = Path(root)
            for name in files:
                file_path = root_path / name
                arcname = file_path.relative_to(source_dir)
                zf.write(file_path, arcname)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Created a clone of NextGenWealth that has namespace substitutions"
    )
    parser.add_argument(
        "--namespace",
        default="FinServ",
        help="Namespace to substitute for FinServ (default: FinServ)",
    )
    args = parser.parse_args()

    namespace = args.namespace

    script_dir = Path(__file__).resolve().parent
    os.chdir(script_dir)

    source_dir = script_dir / "NextGenWealth"
    if not source_dir.is_dir():
        print(f"ERROR: Source directory not found: {source_dir}", file=sys.stderr)
        return 1

    tmp_dir = Path(tempfile.gettempdir())
    dest_dir = tmp_dir / "ClonedNextGenWealth"

    if dest_dir.exists():
        raise FileExistsError(f"Destination already exists: {dest_dir}")

    shutil.copytree(source_dir, dest_dir)

    substitutions = [
        ("FinServ__", f"{namespace}__"),
        ("FinServ:", f"{namespace}:"),
    ]
    for root, _dirs, files in os.walk(dest_dir):
        root_path = Path(root)
        for name in files:
            file_path = root_path / name
            for old_token, new_token in substitutions:
                replace_in_file(file_path, old_token, new_token)

    datakit_dir = dest_dir / "DataKit"
    datakit_zip = dest_dir / "DataKitSinglePackage.zip"
    if datakit_dir.is_dir():
        zip_directory_contents(datakit_dir, datakit_zip)

    package_resources_dir = dest_dir / "PackageResources"
    package_resources_zip = dest_dir / "PackageResourcesSinglePackage.zip"
    if package_resources_dir.is_dir():
        zip_directory_contents(package_resources_dir, package_resources_zip)

    print(f"Created {dest_dir}")
    print(f"Created {datakit_zip}")
    print(f"Created {package_resources_zip}")
    print(f"Namespace {namespace}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
