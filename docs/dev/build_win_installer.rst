Create Windows Installer
========================

For building an installer, we use NSIS.

* Install NSIS: https://nsis.sourceforge.io/Download

* Copy SQLite3 DLL::

    cp ..

* In the MingW64 environment, launch the compilation process::

    makensis bin/installer.nsi

* The generated ``.exe`` is located in ``./bin`` folder.
