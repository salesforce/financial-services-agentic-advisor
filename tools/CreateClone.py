#!/usr/bin/env python3
"""Create an sf project called ClonedAgenticAdvisorForFinancialServices to deploy
artifacts needed for agentic advisor on the financial services wealth package."""

import argparse
import os
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path


def replace_namespace(root_dir, namespace):
    """Replace 'FinServ__' with '<namespace>__' in every (text) file under root_dir."""
    replacement = namespace + "__"
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            path = os.path.join(dirpath, filename)
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    content = fh.read()
            except (UnicodeDecodeError, OSError):
                continue
            if "FinServ__" in content:
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(content.replace("FinServ__", replacement))


def zip_directory_contents(source_dir, zip_path):
    """Zip contents of source_dir so entries (including package.xml) are at archive root."""
    source_dir = Path(source_dir)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _dirs, files in os.walk(source_dir):
            root_path = Path(root)
            for name in files:
                file_path = root_path / name
                arcname = file_path.relative_to(source_dir)
                zf.write(file_path, arcname)
    return os.path.abspath(zip_path)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Create an sf project called ClonedAgenticAdvisorForFinancialServices "
            "to deploy artifacts needed for agentic advisor on the financial "
            "services wealth package."
        )
    )
    parser.add_argument(
        "--namespace",
        default="FinServ",
        help="namespace prefix to apply (defaults to FinServ)",
    )
    parser.add_argument(
        "--target-directory",
        default=tempfile.gettempdir(),
        help=(
            "directory to create ClonedAgenticAdvisorForFinancialServices in "
            "(defaults to TMPDIR)"
        ),
    )
    args = parser.parse_args()

    # cd into the folder that is the parent of CreateClone.py.
    tools_dir = Path(__file__).resolve().parent
    os.chdir(tools_dir)

    # AgenticAdvisor lives in the repo root (parent of tools/).
    source_dir = tools_dir.parent / "AgenticAdvisor"

    clone_dir = os.path.abspath(
        os.path.join(args.target_directory, "ClonedAgenticAdvisorForFinancialServices")
    )

    if os.path.exists(clone_dir):
        sys.exit(f"Error: {clone_dir} already exists")

    # Equivalent of: cp -r AgenticAdvisor <target-directory>/ClonedAgenticAdvisorForFinancialServices
    shutil.copytree(source_dir, clone_dir)

    os.chdir(clone_dir)

    if args.namespace != "FinServ":
        replace_namespace(clone_dir, args.namespace)

    datakit_zip = zip_directory_contents(
        "DataKit", "DataKitSinglePackage.zip"
    )
    package_resources_zip = zip_directory_contents(
        "PackageResources", "PackageResourcesSinglePackage.zip"
    )

    print(f"Created sf project: {clone_dir}")
    print(f"DataKit Zip file: {datakit_zip}")
    print(f"PackageResources Zip file: {package_resources_zip}")
    print(f"namespace: {args.namespace}")


if __name__ == "__main__":
    main()
