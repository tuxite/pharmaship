Pharmaship
==========

A pharmacy software for merchant ships.

This software is in active development!

## Documentation & Installation
Documentation, installation and usage, is available on
http://pharmaship.rtfd.org or directly on ``docs/build/html/index.html``.

## Install on Linux

Following packages are needed for `pip install`:

* `libcairo-dev`
* `python3-dev`
* `libgirepository1.0-dev`

After installing missing system dependencies, use a `virtualenv`.

Following packages are needed to compile GResources:

* `libglib2.0-dev-bin` (provides `glib-compile-resources`)
* `libxml2-utils` (provides `xmllint`)

## First run

In the virtual environment:

    $ pip install pharmaship-0.1.tar.gz


> All dependencies should install normally

Prepare the database:

    $ pharmaship-admin migrate
    $ pharmaship-admin populate

Then launch the graphical interface:

    $ pharmaship
