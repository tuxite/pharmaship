#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""File deduplication using jdupes generated file.

Call jdupes:
  jdupes -r -S -j -o name -X onlyext:dll,DLL build/win64 > duplicates.json
"""
import json
from pathlib import Path

# Extensions to consider
EXTENSIONS = [
    ".dll",
    ".DLL",
]

total_size = 0

with open("duplicates.json", "r") as fdesc:
    data = json.load(fdesc)

abs_path = Path("build/win64")

for item in data["matchSets"]:
    if Path(item["fileList"][-1]["filePath"]).suffix not in EXTENSIONS:
        continue

    nb_files = 0

    # Check if the first duplicated is at the "root" of the package
    # if yes, allow deletion of other located duplicate.
    rel_path = Path(item["fileList"][0]["filePath"])
    if abs_path / rel_path.name == rel_path:
        _delete = True
    else:
        _delete = False

    for path in item["fileList"][1:]:
        if _delete is True:
            Path(path["filePath"]).unlink(missing_ok=True)
            nb_files += 1
        continue

    total_size += item["fileSize"] * nb_files

print(total_size)
