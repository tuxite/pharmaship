# -*- coding: utf-8; -*-
import django.utils.text

def filepath(instance, filename):
    """Returns a file path using the instance name.

    Used in :model:`inventory.Equipment`.
    """
    # Keeps the extension of the uploaded file
    # TODO: Find a better way to detect the extension.
    extension = filename.split('.')[-1]

    name = django.utils.text.slugify(instance.name)  # Safer
    return "pictures/users/{0}.{1}".format(name, extension)