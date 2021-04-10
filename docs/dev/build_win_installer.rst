Create Windows Installer
========================

First you need to create the Python environment with MSYS/Mingw64 as described
in this page.

For building an installer, we use NSIS (already installed in the previous
step).

* Remove non-necessary files that can cause freezing failure::

    rm -rf venv/lib/python3.8/site-packages/setuptools*
    rm -rf venv/lib/python3.8/site-packages/pip*
    rm -rf venv/lib/python3.8/site-packages/wheel*


* Patch CairoSVG and Weasyprint for freezing::

    mingw32-make patch_cairosvg
    mingw32-make patch_weasyprint

* Install JDupes (https://github.com/jbruchon/jdupes) for deduplication::

    wget -c -O "jdupes.zip" "https://github.com/jbruchon/jdupes/releases/download/v1.19.1/jdupes-1.19.1-win64.zip"
    unzip -j "jdupes.zip" "*/jdupes.exe" -d "./bin"
    rm jdupes.zip

* Compile translation files::

    mingw32-make mo

* Load allowances to be embeded in the installer::

    mkdir allowances
    cd allowances
    tar -xvf <your_allowances.tar.xz>
    cd ..

* Build the installer::

    mingw32-make win64

* The generated ``.exe`` is located in ``./bin`` folder.
