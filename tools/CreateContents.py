#!/usr/bin/env python3
import os
import xml.etree.ElementTree as ET
from collections import namedtuple
from pathlib import Path

# cd into the folder that holds NextGenWealth, then into NextGenWealth.
# Path(__file__).resolve().parent is tools/; its parent is the repo root, which
# is where NextGenWealth lives (so `cd NextGenWealth` below resolves).
os.chdir(Path(__file__).resolve().parent.parent)
os.chdir("NextGenWealth")

ArtifactInfo = namedtuple("ArtifactInfo", ["type", "name", "label", "description"])


class Artifact:
    def __init__(self, info):
        self.info = info
        self.num_incoming = 0
        self.outgoing = []  # array of Artifact


def local(tag):
    """Strip the XML namespace, e.g. '{...}label' -> 'label'."""
    return tag.rsplit("}", 1)[-1]


def build_artifact_map():
    artifact_map = {}  # map of string (bare name) to Artifact
    for dirpath, _, filenames in os.walk("."):
        for filename in filenames:
            if not filename.endswith("-meta.xml"):
                continue

            # type: directory name with the trailing 's' removed
            folder = os.path.basename(dirpath)
            type_ = folder[:-1] if folder.endswith("s") else folder

            # name: filename with the .<ext>-meta.xml extension fully removed,
            # i.e. the bare developer name. This is also the map key.
            name = filename[: -len("-meta.xml")].rsplit(".", 1)[0]
            key = name

            root = ET.parse(os.path.join(dirpath, filename)).getroot()

            # label comes from <masterLabel>, <label>, or <name> at the top level
            label = None
            children = {local(c.tag): c for c in root}
            for candidate in ("masterLabel", "label", "name"):
                if candidate in children:
                    label = (children[candidate].text or "").strip()
                    break
            if label is None:
                raise ValueError(f"No label found for {name}")

            # description from top-level <description>, may be None
            description = None
            if "description" in children:
                description = (children["description"].text or "").strip()

            if key in artifact_map:
                existing = artifact_map[key].info.type
                raise ValueError(
                    f"Duplicate artifact {name} which is both a {existing} and {type_}"
                )

            artifact_map[key] = Artifact(ArtifactInfo(type_, name, label, description))

    return artifact_map


def find_roots(artifact_map):
    # Scan every tag in every file; if a tag's value matches an artifact key,
    # record an edge (parent_name, child_name).
    edges = []
    for dirpath, _, filenames in os.walk("."):
        for filename in filenames:
            if not filename.endswith("-meta.xml"):
                continue
            parent_key = filename[: -len("-meta.xml")].rsplit(".", 1)[0]
            root = ET.parse(os.path.join(dirpath, filename)).getroot()
            for el in root.iter():
                value = (el.text or "").strip()
                if value.startswith("flow://"):
                    value = value[len("flow://"):]
                if value in artifact_map and value != parent_key:
                    edges.append((parent_key, value))

    # Apply edges: parent gains an outgoing child, child gains an incoming count.
    for parent_key, child_key in edges:
        parent = artifact_map[parent_key]
        child = artifact_map[child_key]
        parent.outgoing.append(child)
        child.num_incoming += 1

    # Roots are artifacts nothing points at.
    return [a for a in artifact_map.values() if a.num_incoming == 0]


def cap(s):
    # Capitalize only the first letter (genAiPromptTemplate -> GenAiPromptTemplate),
    # then display GenAiPromptTemplate as PromptTemplate.
    capped = s[:1].upper() + s[1:]
    if capped == "GenAiPromptTemplate":
        return "PromptTemplate"
    return capped


def emit(artifact, depth, lines):
    indent = "  " * depth
    lines.append(f"{indent}- {artifact.info.label} ({cap(artifact.info.type)})")
    for child in artifact.outgoing:
        child.num_incoming -= 1
        emit(child, depth + 1, lines)


def main():
    artifact_map = build_artifact_map()
    roots = find_roots(artifact_map)

    lines = ["# Contents", ""]
    for root in roots:
        emit(root, 0, lines)

    # Anything still > 0 was never reached from a root -> cycle.
    for artifact in artifact_map.values():
        if artifact.num_incoming > 0:
            raise ValueError(f"Cycle detected involving {artifact.info.name}")

    with open("../CONTENTS.md", "w") as fh:
        fh.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
