Create Debian package
=====================

The Debian script uses ``dh-virtualenv``
(https://github.com/spotify/dh-virtualenv) to build the application structure
including some PyPi packages that are not (yet) distributed in Debian.

No need to be inside a virtual environment.

1. Install the build dependencies::

    # In the pharmaship folder
    sudo mk-build-deps -ri

2. Build the ``pharmaship`` debian package::

    dpkg-buildpackage -us -uc -b

3. Once finished, the generated Debian package is located::

    ../pharmaship_<version>.deb
