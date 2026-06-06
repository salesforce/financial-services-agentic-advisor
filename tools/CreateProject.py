#!/usr/bin/env python3
"""Create a project to called ClonedcNextGenWealth to deploy the next gen wealth project."""
import argparse
import os
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

# import the helpers from the sibling script. Importing it runs CreateContents'
# module-level os.chdir (into the source NextGenWealth); we reset the cwd in
# main() before using it, so that side effect is harmless here.
import CreateContents


def metadata_type(type_):
    """Capitalize the first letter for the package.xml <name> (flow -> Flow)."""
    return type_[:1].upper() + type_[1:]


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
                # skip anything that isn't readable utf-8 text
                continue
            if "FinServ__" in content:
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(content.replace("FinServ__", replacement))


def collect_members(roots):
    """Walk roots, descending into outgoing, returning {type: [names...]} in order."""
    collected = {}  # type -> list of names (ordered, deduped)
    seen = set()  # ids of visited artifacts

    def walk(artifact):
        if id(artifact) in seen:
            return
        seen.add(id(artifact))
        names = collected.setdefault(artifact.info.type, [])
        name = artifact.info.name
        if name not in names:
            names.append(name)
        for child in artifact.outgoing:
            walk(child)

    for root in roots:
        walk(root)
    return collected


def build_package_xml(collected):
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<Package xmlns="http://soap.sforce.com/2006/04/metadata">',
    ]
    for type_, names in collected.items():
        lines.append("    <types>")
        lines.append(f"        <name>{metadata_type(type_)}</name>")
        for name in names:
            lines.append(f"        <members>{name}</members>")
        lines.append("    </types>")
    lines.append("    <version>67.0</version>")
    lines.append("</Package>")
    return "\n".join(lines) + "\n"


def build_single_package_zip(clone_dir):
    """Zip package.xml and all folders in clone_dir into SinglePackage.zip."""
    zip_path = os.path.join(clone_dir, "SinglePackage.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # package.xml at the root of the archive
        zf.write("package.xml", "package.xml")
        # all folders, recursively
        for entry in sorted(os.listdir(".")):
            if not os.path.isdir(entry):
                continue
            for dirpath, _, filenames in os.walk(entry):
                for filename in filenames:
                    full = os.path.join(dirpath, filename)
                    zf.write(full, os.path.relpath(full, "."))
    return zip_path


def main():
    parser = argparse.ArgumentParser(
        description="Create a project to called ClonedcNextGenWealth to deploy the next gen wealth project"
    )
    parser.add_argument(
        "--namespace",
        default="FinServ",
        help="namespace prefix to apply (defaults to FinServ)",
    )
    parser.add_argument(
        "--exclude",
        default="",
        help="comma separated list of types to exclude with no spaces before/after the comma",
    )
    parser.add_argument(
        "--target-directory",
        default=tempfile.gettempdir(),
        help="directory to create ClonedNextGenWealth in (defaults to TMPDIR)",
    )
    args = parser.parse_args()

    # cd into the folder that holds NextGenWealth. CreateProject.py lives in tools/,
    # so its parent's parent (the repo root) is where NextGenWealth lives, which
    # mirrors how CreateContents.py resolves its own location.
    repo_root = Path(__file__).resolve().parent.parent
    os.chdir(repo_root)

    # Resolve the clone destination to an absolute path so later chdir calls don't
    # invalidate it.
    clone_dir = os.path.abspath(
        os.path.join(args.target_directory, "ClonedNextGenWealth")
    )

    # Error out if <target-directory>/ClonedNextGenWealth already exists.
    if os.path.exists(clone_dir):
        sys.exit(f"Error: {clone_dir} already exists")

    # cp -r NextGenWealth <target-directory> (renamed to ClonedNextGenWealth).
    shutil.copytree("NextGenWealth", clone_dir)

    # cd NextGenWealth (source), then build the artifact map from the source tree.
    os.chdir("NextGenWealth")
    artifact_map = CreateContents.build_artifact_map()

    # cd to the ClonedNextGenWealth folder created above.
    os.chdir(clone_dir)

    # If namespace is anything other than FinServ, rewrite the FinServ__ prefix.
    if args.namespace != "FinServ":
        replace_namespace(clone_dir, args.namespace)

    # find_roots reads files relative to the cwd (the clone).
    roots = CreateContents.find_roots(artifact_map)

    # Drop any root whose type is one of the excluded types (case-insensitive).
    exclude_types = [t.lower() for t in args.exclude.split(",") if t]
    for excluded in exclude_types:
        # remove excluded artifact and it's children
        roots = [r for r in roots if r.info.type.lower() != excluded]

    # Walk the remaining roots and overwrite package.xml in the clone location.
    collected = collect_members(roots)
    with open("package.xml", "w", encoding="utf-8") as fh:
        fh.write(build_package_xml(collected))

    # cd ClonedNextGenWealth and zip package.xml and all folders into SinglePackage.zip.
    os.chdir(clone_dir)
    zip_path = build_single_package_zip(clone_dir)

    print(f"Created sf project {clone_dir}")
    print(f"Zip file {zip_path}")
    print(f"namespace={args.namespace}")
    print(f"exclude={args.exclude}")


if __name__ == "__main__":
    main()
