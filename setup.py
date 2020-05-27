#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup file for Pharmaship.

A WeasyPrint file must be edited for cx_Freeze:

weasyprint/__init__.py:

    if hasattr(sys, 'frozen'):
        if hasattr(sys, '_MEIPASS'):
            # Frozen with PyInstaller
            # See https://github.com/Kozea/WeasyPrint/pull/540
            ROOT = Path(sys._MEIPASS)
        else:
            # Frozen with something else (py2exe, etc.)
            # See https://github.com/Kozea/WeasyPrint/pull/269
    --      ROOT = os.path.dirname(sys.executable)
    ++      ROOT = Path(os.path.dirname(sys.executable)) / "lib" / "weasyprint"
    else:
        ROOT = Path(os.path.dirname(__file__))

    VERSION = __version__ = (ROOT / 'VERSION').read_text().strip()

cairosvg/__init__.py:

    if hasattr(sys, 'frozen'):
        if hasattr(sys, '_MEIPASS'):
            # Frozen with PyInstaller
            # See https://github.com/Kozea/WeasyPrint/pull/540
            ROOT = Path(sys._MEIPASS)
        else:
            # Frozen with something else (py2exe, etc.)
            # See https://github.com/Kozea/WeasyPrint/pull/269
    --      ROOT = Path(os.path.dirname(sys.executable))
    ++      ROOT = Path(os.path.dirname(sys.executable)) / "lib" / "cairosvg"
    else:
        ROOT = Path(os.path.dirname(__file__))

    VERSION = __version__ = (ROOT / 'VERSION').read_text().strip()

"""
import sys
# import platform
import pkg_resources
import os
import os.path
from pathlib import Path, PurePath

# from setuptools import setup, find_packages
from setuptools import find_packages
from cx_Freeze import setup, Executable

with open("README.md", "r") as fh:
    long_description = fh.read()

SEARCH_PATHS = os.getenv("PATH", os.defpath).split(os.pathsep)

DISTRIBUTIONS = [
    "rest-framework-generic-relations",
    "munch",
]

DLL_WIN = [
    'libgtk-3-0.dll',
    'libgdk-3-0.dll',
    'libepoxy-0.dll',
    'libgdk_pixbuf-2.0-0.dll',
    'libpango-1.0-0.dll',
    'libpangocairo-1.0-0.dll',
    'libpangoft2-1.0-0.dll',
    'libpangowin32-1.0-0.dll',
    'libatk-1.0-0.dll',
    'libxml2-2.dll',
    'librsvg-2-2.dll',
]

GNUPG_WIN = [
    "gpg.exe",
    "libiconv-2.dll",
]

GDBUS_WIN = [
    ("gdbus.exe", PurePath("lib/gi")),
    "gdbus.exe",
]

EXECUTABLE_WIN = [
    Executable(
        script="bin/launcher.py",
        targetName="pharmaship.exe",
        base="Win32GUI",
        icon="bin/pharmaship.ico"
    ),
    Executable(
        script="bin/manage.py",
        targetName="pharmaship-admin.exe",
        base="Console",
    )
]

EXECUTABLE = [
    Executable(
        script="bin/launcher.py",
        targetName="pharmaship",
        base=None,
        icon="bin/pharmaship.ico"
    ),
    Executable(
        script="bin/manage.py",
        targetName="pharmaship-admin",
        base="Console",
    )
]

EXCLUDE_ICONS = [
    "apps",
    "emblems",
    "emotes",
    "legacy",
    "status"
]

def collect_dist_info(packages):
    """Recursively collects the path to the packages' dist-info."""
    if not isinstance(packages, list):
        packages = [packages]
    dirs = []
    for pkg in packages:
        distrib = pkg_resources.get_distribution(pkg)
        for req in distrib.requires():
            dirs.extend(collect_dist_info(req.key))
        dirs.append((
            distrib.egg_info,
            PurePath('lib') / PurePath(distrib.egg_info).name
            ))

    return dirs


def cairocffi_files():
    """Add cairocffi._generated files."""
    __module_name = "cairocffi"
    distrib = pkg_resources.get_distribution(__module_name)
    module_path = Path(distrib.location) / __module_name / "_generated"

    files = []
    dest_path = PurePath("lib") / __module_name / "_generated"

    for file in module_path.glob('*.py'):
        filename = module_path / file
        if not filename.is_file():
            continue
        files.append((filename, dest_path / filename.name))

    return files


def pillow_libs_files():
    """Recursively add cairocffi._generated files."""
    __module_name = "Pillow.libs"
    distrib = pkg_resources.get_distribution("Pillow")
    module_path = Path(distrib.location) / __module_name
    print(module_path)
    files = []
    dest_path = PurePath("lib") / __module_name

    for file in module_path.glob('**/*'):
        filename = module_path / file
        if not filename.is_file():
            continue
        print(filename)
        print(file)
        files.append((filename, dest_path / file))

    return files


def get_file(filename):
    """Return full path for filename."""
    for p in SEARCH_PATHS:
        p = os.path.join(p, filename)
        if os.path.isfile(p):
            return p

    return None


def collect_files(items):
    """Collect items and create tuple(origin, destination)."""
    files = []
    for item in items:
        if isinstance(item, tuple):
            name = item[0]
            root = item[1]
        else:
            name = item
            root = PurePath(".")

        path = get_file(name)
        if not path:
            print("File not found: %s", name)
            continue
        files.append((path, root/name))

    return files


def collect_icons():
    """Collect GTK theme icons."""
    # TODO: list only necessary icons
    files = []

    path = Path(r"C:\msys64\mingw64\share\icons\Adwaita")
    dest = PurePath("share/icons/Adwaita")

    for file in path.glob("**/*symbolic.*"):
        if file.parts[-2] in EXCLUDE_ICONS:
            continue
        rel_path = file.relative_to(path)
        files.append((file, dest / rel_path))

    for file in path.glob("**/index.theme"):
        rel_path = file.relative_to(path)
        files.append((file, dest / rel_path))

    # Specific for "spinner"
    name = "scalable-up-to-32/status/process-working-symbolic.svg"
    files.append((path / name, dest / name))
    
    return files


def get_collected_files():
    """Return the list of data files to copy in the bundle."""
    collected_files = []
    if sys.platform == "win32":
        collected_files = [
            *collect_dist_info(DISTRIBUTIONS),
            *collect_icons(),
            *collect_files(GDBUS_WIN),
            *collect_files(GNUPG_WIN),
            *collect_files(DLL_WIN),
            # cairocffi generated files
            *cairocffi_files(),
            # Pillow.libs
            *pillow_libs_files(),
            # GLib schemas
            (r"C:\msys64\mingw64\share\glib-2.0\schemas", r"share\glib-2.0\schemas"),
            # Namespaces
            (r"C:\msys64\mingw64\lib\girepository-1.0", r"lib\girepository-1.0"),
            # GdkPixbuf loaders
            (r"C:\msys64\mingw64\lib\gdk-pixbuf-2.0", r"lib\gdk-pixbuf-2.0"),
            # FontConfig
            (r"C:\msys64\mingw64\share\fontconfig", r"share\fontconfig"),
            (r"C:\msys64\mingw64\etc\fonts", r"etc\fonts"),
        ]
    else:
        collected_files = [
            *collect_dist_info(DISTRIBUTIONS),
            # cairocffi generated files
            *cairocffi_files(),
            # Pillow.libs
            *pillow_libs_files(),
        ]
    return collected_files


def get_build_path():
    """Return build path according to the system platform."""
    if sys.platform == "win32":
        return "build/win64"
    else:
        return "build/linux64"


def get_exe_config():
    """Return build path according to the system platform."""
    if sys.platform == "win32":
        return EXECUTABLE_WIN
    else:
        return EXECUTABLE


# cx_Freeze fine tuning
build_exe_options = {
    "zip_include_packages": [
        "django",
        "pytz",
        ],
    "packages": [
        "statistics",
        "gi",
        "six",
        "cairocffi",
        "django",
        "rest_framework",
        "mptt",
        "generic_relations",
        "cairosvg",
        "weasyprint",
        "munch",
        "cerberus",
        "coloredlogs",
        "gnupg",
        "yaml",
        "PyPDF2",
        "pharmaship",
        ],
    "excludes": [
        "tkinter",
        "Tkinter",
        "test",
        ],
    "include_files": get_collected_files(),
    "build_exe": get_build_path(),
    "optimize": 2
    }


setup(
    name="pharmaship",
    description="A ship's pharmacy inventory software.",
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Django",
        "django-mptt",
        "djangorestframework",
        "rest-framework-generic-relations",
        "munch",
        "Cerberus",
        "coloredlogs",
        "PyGObject",
        "WeasyPrint",
        "python-gnupg",
        "PyYAML",
        "PyPDF2"
    ],
    scripts=[
        "bin/pharmaship-sign"
    ],
    entry_points={
        'console_scripts': [
            'pharmaship=pharmaship.core.management.commands.gui:main',
            'pharmaship-admin=pharmaship.manage:main'],
    },
    executables=get_exe_config(),
    options={
        "build_exe": build_exe_options,
        },
    # metadata to display on PyPI
    author="Matthieu Morin",
    author_email="morinmatthieu@gmail.com",
    # keywords="hello world example examples",
    url="http://pharmaship.rtfd.org",   # project home page, if any
    # project_urls={
    #     "Bug Tracker": "https://bugs.example.com/HelloWorld/",
    #     "Documentation": "https://docs.example.com/HelloWorld/",
    #     "Source Code": "https://code.example.com/HelloWorld/",
    # },
    # classifiers=[
    #     "License :: OSI Approved :: Python Software Foundation License"
    # ]
)
