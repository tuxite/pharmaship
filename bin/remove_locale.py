#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""File deduplication using jdupes generated file.

Call jdupes: bin/jdupes.exe -r -S -j build/win64 > duplicates.json
"""
import json
from pathlib import Path

LOCALES = [
    "fr",
    "en"
]

total_size = 0 
 
for item in Path("build/win64/lib").glob("**/*.mo"):
    lc_messages_index = item.parts.index("LC_MESSAGES")
    found = False
    for locale in LOCALES:
        if locale in item.parts[lc_messages_index - 1]:
            found = True
            continue
    if found is True:
        continue
    
    total_size += item.stat().st_size
    item.unlink()
        
for item in Path("build/win64/lib/pyphen").glob("**/*.dic"):
    found = False
    for locale in LOCALES:
        if locale in item.stem:
            found = True
            continue
    if found is True:
        continue
    
    total_size += item.stat().st_size
    item.unlink()

print(total_size)
    