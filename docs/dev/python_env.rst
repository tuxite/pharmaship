Set-up Python Environment
=========================

Linux
-----
The use of a virtual environment is strongly encouraged.

Following packages may be needed for ``pip install``:

    * ``libcairo-dev``
    * ``python3-dev``
    * ``libgirepository1.0-dev``

::

    sudo apt install libcairo-dev python3-dev libgirepository1.0-dev

After installing missing system dependencies, it is strongly recommended to use
a virtual environment.

Following packages may be needed to compile GResources:

    * ``libglib2.0-dev-bin`` (provides ``glib-compile-resources``)
    * ``libxml2-utils`` (provides ``xmllint``)

::

    sudo apt install libglib2.0-dev-bin libxml2-utils


Then, in the virtual environment::

    pipenv install pharmaship-0.1.tar.gz


*All dependencies should install normally...*

Windows
-------
This procedure has been tested on Windows 10.

MSYS Environment
^^^^^^^^^^^^^^^^

  * Go to http://www.msys2.org/ and download the x86_64 installer
  * Follow the instructions on the page for setting up the basic environment
  * Run ``C:\msys64\mingw64.exe`` - a terminal window should pop up
  * Execute::

      pacman -Suy

*Starting from now, all commands are launched into the MingW64 environment.*


Dependencies
^^^^^^^^^^^^
* Install following MingW64 packages:

  * ``mingw-w64-x86_64-gcc``
  * ``mingw-w64-x86_64-make``
  * ``mingw-w64-x86_64-gnupg``
  * ``mingw-w64-x86_64-zlib``
  * ``mingw-w64-x86_64-gtk3``
  * ``mingw-w64-x86_64-gobject-introspection``
  * ``mingw-w64-x86_64-adwaita-icon-theme``
  * ``mingw-w64-x86_64-nsis``
  * ``mingw-w64-x86_64-python-pip``
  * ``mingw-w64-x86_64-python-virtualenv``
  * ``mingw-w64-x86_64-python-pillow``
  * ``mingw-w64-x86_64-python-cairo``
  * ``mingw-w64-x86_64-python-matplotlib``
  * ``mingw-w64-x86_64-python-numpy``
  * ``mingw-w64-x86_64-python-pandas``

  *This will install Python 3.9+ and associated packages necessary for Pharmaship
  development.*


::

  pacman -S mingw-w64-x86_64-gcc mingw-w64-x86_64-make mingw-w64-x86_64-gnupg mingw-w64-x86_64-zlib mingw-w64-x86_64-gtk3 mingw-w64-x86_64-gobject-introspection mingw-w64-x86_64-adwaita-icon-theme mingw-w64-x86_64-nsis mingw-w64-x86_64-python-pip mingw-w64-x86_64-python-virtualenv mingw-w64-x86_64-python-pillow mingw-w64-x86_64-python-cairo mingw-w64-x86_64-python-matplotlib mingw-w64-x86_64-python-numpy mingw-w64-x86_64-python-pandas

* These dependencies may be necessary:

  * ``git``
  * ``patch``
  * ``wget``
  * ``unzip``
  * ``tar``

::

  pacman -S git patch wget unzip tar

Create a virtual environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* Create the project folder (assuming you are in ``C:\msys64\home\<User>``)::

      mkdir pharmaship
      cd pharmaship

* Extract pharmaship archive in a folder (assuming you named it ``pharmaship``).

* Create the virtual environment and install dependencies::

      virtualenv --system-site-packages venv

      venv/bin/python -m pip install -r requirements.txt
      venv/bin/python -m pip install winpath
      venv/bin/python -m pip install cx_Freeze
      venv/bin/python -m pip install --platform win_amd64 --only-binary=:all: --target venv/lib/python3.8/site-packages --upgrade pywin32

*This will install all dependencies for Pharmaship and Windows-specific
dependencies. In addition, it installs cx_Freeze for freezing the python
environment in order to create the Windows installer.*

First run
---------

Then launch the graphical interface::

    venv/bin/python launch.py


Or launch additional commands with::

    venv/bin/python manage.py
