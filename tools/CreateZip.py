#!/usr/bin/env python3
"""Create NextGenWealth.zip in the tmp folder."""
import argparse
import os
import shutil
import tempfile
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
    collected = {}  # type -> list of bare names (ordered, deduped)
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


def main():
    parser = argparse.ArgumentParser(
        description="Create NextGenWealth.zip in the tmp folder"
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
        "--create-zip",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="zip the tmp NextGenWealth folder (defaults to true)",
    )
    args = parser.parse_args()

    # cd into the folder that holds NextGenWealth. CreateZip.py lives in tools/,
    # so its parent's parent (the repo root) is where NextGenWealth lives, which
    # mirrors how CreateContents.py resolves its own location.
    repo_root = Path(__file__).resolve().parent.parent
    os.chdir(repo_root)

    # cp -r NextGenWealth $TMPDIR  (tempfile.gettempdir() is the cross-platform TMPDIR)
    tmpdir = tempfile.gettempdir()
    dest = os.path.join(tmpdir, "NextGenWealth")
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree("NextGenWealth", dest)

    # cd NextGenWealth (source), then build the artifact map from the source tree.
    os.chdir("NextGenWealth")
    artifact_map = CreateContents.build_artifact_map()

    # cd to the tmp NextGenWealth folder created above.
    os.chdir(dest)

    # If namespace is anything other than FinServ, rewrite the FinServ__ prefix.
    if args.namespace != "FinServ":
        replace_namespace(dest, args.namespace)

    # find_roots reads files relative to the cwd (the tmp copy).
    roots = CreateContents.find_roots(artifact_map)

    # Drop any root whose type is one of the excluded types (case-insensitive).
    exclude_types = [t.lower() for t in args.exclude.split(",") if t]
    for excluded in exclude_types:
        roots = [r for r in roots if r.info.type.lower() != excluded]

    # Walk the remaining roots and overwrite package.xml in this tmp location.
    collected = collect_members(roots)
    with open("package.xml", "w", encoding="utf-8") as fh:
        fh.write(build_package_xml(collected))

    print(f"Created {dest} for namespace={args.namespace} and exclude={args.exclude}")

    if args.create_zip:
        zip_base = os.path.join(tmpdir, "NextGenWealth")
        zip_path = shutil.make_archive(
            zip_base, "zip", root_dir=tmpdir, base_dir="NextGenWealth"
        )
        print(f"Created zip archive {zip_path}")


if __name__ == "__main__":
    main()
