#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""File deduplication using jdupes generated file.

Call jdupes: bin/jdupes.exe -r -S -j build/win64 > duplicates.json
"""
import json
from pathlib import Path

# Extensions to consider
EXTENSIONS = [
    ".dll",
]

total_size = 0 

with open("duplicates.json", "r") as fdesc:
    data = json.load(fdesc)  

abs_path = Path("build/win64")

for item in data["matchSets"]:
    if Path(item["fileList"][-1]["filePath"]).suffix not in EXTENSIONS:
        continue
    
    nb_files = 0
    
    # Check if the last duplicated is at the "root" of the package
    # if yes, allow deletion of PIL located duplicate.
    rel_path = Path(item["fileList"][-1]["filePath"])
    if abs_path / rel_path.name == rel_path:
        pil_delete = True
    else:
        pil_delete = False
        
    for path in item["fileList"][0:-1]:
        if "PIL" in path["filePath"]:
            if pil_delete is True:
                Path(path["filePath"]).unlink(missing_ok=True)
                nb_files += 1
            continue

        Path(path["filePath"]).unlink(missing_ok=True)
        
        nb_files += 1
    
    total_size += item["fileSize"] * nb_files

print(total_size)
    