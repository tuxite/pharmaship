#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generate custom installer files for NSIS."""
import gnupg
import tarfile
import coloredlogs
import logging
import shutil

import yaml
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


from pathlib import Path
from io import BytesIO

import django
from django.template import Template, Context
from django.conf import settings

from prompt_toolkit.shortcuts import checkboxlist_dialog, radiolist_dialog

# Logging support
log = logging.getLogger("pharmaship")
coloredlogs.install(level='DEBUG', logger=log)

# In order to use Template engine of Django, we must initialize it with
# minimum settings
settings.configure(TEMPLATES=[{
    'BACKEND': 'django.template.backends.django.DjangoTemplates'
}])
django.setup()

# Detect the base directory
BASE_DIR = Path.cwd()
if BASE_DIR.parts[-1] == "bin":
    BASE_DIR = BASE_DIR.parent

# Database file location and template
DB_FILE = BASE_DIR / "bin" / "database.nsh"
DB_TEMPLATE = Template("""
Section "Database" SecDatabase
  !insertmacro Database "{{ db_file }}"
SectionEnd
""")

# Allowances file location and template
ALLOWANCES_FILE = BASE_DIR / "bin" / "allowances.nsh"
ALLOWANCES_TEMPLATE = Template("""
SectionGroup "Allowances" SecAllowances
  {% for item in allowances %}
  Section "!{{ item.name }}"
    !insertmacro Allowance "{{ item.rel_filename }}"
  SectionEnd
  {% endfor %}
SectionGroupEnd
""")


def get_name(filepath):
    """Read the name of the encrypted GPG package.

    Use GPG to decrypt the data, then open the tar file and try to find
    the ``allowance.yaml`` file where the name is stored.

    :param pathlib.Path filepath: Location of the allowance package to read.

    :return: Name of the allowance or None if the file is not compliant.
    :rtype: str or None
    """
    manager = gnupg.GPG(gnupghome=str(BASE_DIR / "bin"))
    data = manager.decrypt(filepath.read_bytes()).data
    if data is None:
        log.warning("Not a valid GPG armored file: %s", filepath)
        return None

    try:
        tar = tarfile.open(fileobj=BytesIO(data), mode="r")
    except (tarfile.ReadError, tarfile.CompressionError) as error:
        log.warning("File is not a valid Tar file. %s", error)
        return None

    try:
        conf = tar.extractfile('inventory/allowance.yaml').read()
    except KeyError:
        log.warning("Not a Pharmaship Allowance package.")
        return None

    try:
        # config = json.loads(content)
        config = yaml.load(conf, Loader=Loader)
    except (ValueError, TypeError, yaml.YAMLError) as error:
        log.warning("Unable to parse the config file. %s", error)
        return None

    try:
        name = config[0]["fields"]["name"]
        version = config[0]["fields"]["version"]
        date = config[0]["fields"]["date"]
    except KeyError:
        log.warning("Invalid YAML file")
        return None

    result = "{0} (version {1}, {2})".format(name, version, date)

    return result


def get_allowances():
    """Return a dictionary of detected allowance packages with their name.

    :return: Dictionary with Path as key and allowance name as value.
    :rtype: dict
    """
    result = {}
    for item in (BASE_DIR / "allowances").glob("*.asc"):
        allowance_name = get_name(item)
        if allowance_name is None:
            continue
        result[item] = allowance_name

    return result


def get_databases():
    """Return a list of all database files found in the base directory.

    It assumes all ``*.db`` and ``*.sqlite3`` are Django compatible.

    :return: List of database files with Path and name.
    :rtype: list(tuple(pathlib.Path, str))
    """
    result = [[None, "None"]]
    for item in BASE_DIR.glob("*.sqlite3"):
        result.append((item, item.name))
    for item in BASE_DIR.glob("*.db"):
        result.append((item, item.name))
    return result


if __name__ == '__main__':
    allowances_values = get_allowances()
    if len(allowances_values) < 1:
        log.warning("No valid allowance found.")
        allowances = None
    else:
        values = [(k, v) for k, v in allowances_values.items()]
        values = sorted(values, key=lambda item: item[1])
        log.debug(values)
        allowances = checkboxlist_dialog(
            title="Allowances",
            text="Select allowances to add to the installer",
            values=values
        ).run()

    database = radiolist_dialog(
        title="Database",
        text="Select database to include to the installer",
        values=get_databases()
    ).run()

    if len(allowances) < 1 and ALLOWANCES_FILE.exists():
        # Backup
        shutil.copyfile(ALLOWANCES_FILE, ALLOWANCES_FILE.with_suffix(".nsh.bak"))
        # Delete the file
        ALLOWANCES_FILE.unlink()

    if database is None and DB_FILE.exists():
        # Backup
        shutil.copyfile(DB_FILE, DB_FILE.with_suffix(".nsh.bak"))
        # Delete the file
        DB_FILE.unlink()

    # Create the allowances file
    data = []
    for allowance in allowances:
        data.append({
            "name": allowances_values[allowance],
            "rel_filename": allowance.relative_to(BASE_DIR / "allowances")
            })
    context = Context({
        "allowances": data
        })

    nsh_string = ALLOWANCES_TEMPLATE.render(context)
    ALLOWANCES_FILE.write_text(nsh_string)

    # Create the database file
    context = Context({
        "db_file": database.relative_to(BASE_DIR)
        })

    nsh_string = DB_TEMPLATE.render(context)
    DB_FILE.write_text(nsh_string)
