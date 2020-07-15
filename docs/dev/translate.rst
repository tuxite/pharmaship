Translate
=========

Pharmaship uses pure ``gettext`` and Django's system for translation.

All ``.pot``, ``.po`` and ``.mo`` file generation is handled in a ``Makefile``.

1. Create translatable file list for gettext::

    make translatable

This will create a file named ``translatable_filelist`` at the project's root.

2. Generate the ``.pot`` files for GUI using gettext::

    make pot

3. Generate the ``.po`` files for the Django project and merge them with \
previously created ``.pot`` files::

    make messages

4. Edit the ``.po`` files in your preferred editor.

5. Generate the ``.mo`` files::

    make mo
