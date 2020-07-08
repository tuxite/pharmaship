Set-up Python Environment
=========================

Linux
-----
The use of a virtual environment is strongly encouraged.

Following packages are needed for ``pip install``:

    * ``libcairo-dev``
    * ``python3-dev``
    * ``libgirepository1.0-dev``

::

    sudo apt install libcairo-dev python3-dev libgirepository1.0-dev

After installing missing system dependencies, use a ``virtualenv``.

Following packages are needed to compile GResources:

    * ``libglib2.0-dev-bin`` (provides ``glib-compile-resources``)
    * ``libxml2-utils`` (provides ``xmllint``)

::

    sudo apt install libglib2.0-dev-bin libxml2-utils


Then, in the virtual environment::

    pip install pharmaship-0.1.tar.gz


*All dependencies should install normally...*

Windows
-------
This procedure has been tested on Windows 7. On Windows 10, the use of WSL may
ease some steps.

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

* Python 3.8 & pip::

    pacman -S mingw-w64-x86_64-python-pip

*This will install Python 3.8+ and associated pip.*

* Install following MingW64 packages:

  * ``mingw-w64-x86_64-gcc``
  * ``mingw-w64-x86_64-python-cairo``
  * ``mingw-w64-x86_64-gobject-introspection``
  * ``mingw-w64-x86_64-python-pillow``
  * ``mingw-w64-x86_64-gnupg``

::

  pacman -S mingw-w64-x86_64-gcc mingw-w64-x86_64-python-cairo mingw-w64-x86_64-gobject-introspection mingw-w64-x86_64-python-pillow mingw-w64-x86_64-gnupg

* These dependencies may be necessary:

  * ``gcc``
  * ``libcrypt-devel``

::

  pacman -S gcc libcrypt-devel

Create a virtual environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Virtualenv::

      pip install virtualenv

* Create the project folder (assuming you are in ``C:\msys64\home\<User>``)::

      mkdir project
      cd project
      virtualenv venv

      . venv/bin/activate

Install Pharmaship and its python dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* Copy pharmaship archive in folder : ``C:\msys64\home\<User>\project``

* Install pip packages::

      venv/bin/python -m pip install cx-Freeze
      venv/bin/python -m pip install pharmaship-0.1.tar.gz

First run
---------

Then launch the graphical interface::

    pharmaship
