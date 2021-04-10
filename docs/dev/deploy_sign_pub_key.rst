Deploy your Signing Public Key
==============================

Pharmaship uses PGP to validate allowance packages signatures.

You must install your signing public key in the Pharmaship install to allow
your users to be able to load your allowances packages.

Import your OpenPGP public key with the following command: ::

  pharmaship-admin key_management add <your_pubkey_filename>


In case ``pharmaship-admin`` is not available: ::

  python manage.py key_management add <your_pubkey_filename>


This can be integrated to your own installer for Windows.
