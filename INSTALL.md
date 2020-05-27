# Install on Windows (for development)

* MSYS
  * Go to http://www.msys2.org/ and download the x86_64 installer
  * Follow the instructions on the page for setting up the basic environment
  * Run `C:\msys64\mingw64.exe` - a terminal window should pop up
  * Execute `pacman -Suy`

> Starting from now, all commands are launched into the MingW64 environment.

* Python 3.8 & pip
  * In MingW64 environment, execute `pacman -S mingw-w64-x86_64-python-pip`.

> This will install Python 3.8+ and associated pip.

* Virtualenv

      pip install virtualenv

* Create the project folder

      mkdir project
      cd project
      virtualenv venv

      . venv/bin/activate

* Copy pharmaship archive in folder : `C:\msys64\home\<User>\project`


* Install following MingW64 packages:
  * `pacman -S mingw-w64-x86_64-gcc`
  * `pacman -S mingw-w64-x86_64-python-cairo`
  * `pacman -S mingw-w64-x86_64-gobject-introspection`
  * `pacman -S mingw-w64-x86_64-python-pillow`
  * `pacman -S mingw-w64-x86_64-gnupg`

  Maybe not necessary:
  * `pacman -S gcc`
  * `pacman -S libcrypt-devel`

* Install pip packages

      venv/bin/python -m pip install cx-Freeze
      venv/bin/python -m pip install pharmaship-0.1.tar.gz

## Create the NSIS installer
* Install NSIS

* Copy SQLite3 DLL:
  cp ..

* Launch compilation process
      makensis bin/installer.nsi


## Interface testing

    pip install dogtail
    ln -s /usr/lib/python3/dist-packages/pyatspi* $VIRTUAL_ENV/lib/python*/site-packages





* Prepare Pharmaship

      pharmaship-admin migrate
      pharmaship-admin populate

* Launch Pharmaship

      pharmaship
