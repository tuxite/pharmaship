# -*- coding: utf-8; -*-
from django.utils.translation import ugettext as _

import tarfile

import io
import os
import hashlib
import importlib

from django.conf import settings

# Signature
from pharmaship.core.gpg import KeyManager
# Logging
from pharmaship.core.utils import log
from pharmaship.core.config import load_config


def extract_manifest(manifest_descriptor):
    """Extract the MANIFEST information and put it into a list of dict."""
    data = manifest_descriptor.readlines()
    result = []
    for item in data:
        f = {}
        f['hash'], f['filename'] = item.decode("ascii").strip().split("  ")
        result.append(f)

    return result


def check_integrity(tar_file):
    """Open the archive and check that the files inside are listed in the
    MANIFEST and the checksum is correct.
    """
    # Open the MANIFEST
    names = tar_file.getnames()
    if "MANIFEST" not in names:
        log.error("MANIFEST not found.")
        return False

    manifest = extract_manifest(tar_file.extractfile("MANIFEST"))
    # TODO: Raise an error when a file (not a directory) in the archive
    # is not in the MANIFEST.
    # Check the SHA256sum
    for item in manifest:
        if item['filename'] not in names:
            log.debug(names)
            log.error("File not in the tar file: %s", item['filename'])
            return False

        m = hashlib.sha256()
        m.update(tar_file.extractfile(item['filename']).read())
        tarfile_hash = m.hexdigest()
        if tarfile_hash != item['hash']:
            log.error("File corrupted: %s", item['filename'])
            return False

    return True


def check_tarfile(data):
    """Check that the data input is a valid Tar file."""
    try:
        tar = tarfile.open(fileobj=io.BytesIO(data), mode="r")
        return tar
    except (tarfile.ReadError, tarfile.CompressionError) as error:
        log.error("File is not a valid Tar file. %s", error)
        return False


def load_module(module):
    try:
        module_pkg = importlib.import_module("pharmaship." + module + ".import_data")
    except ImportError as error:
        log.error("Module %s has no import_data function.", module)
        log.error(error)
        return False

    if not hasattr(module_pkg, "DataImport"):
        log.error("Module %s has no DataImport class.", module)
        return False

    module_class = module_pkg.DataImport
    return module_class


def load_function(module):
    pass


class Importer:
    """Class used to import a data file in Onboard Assistant."""

    def __init__(self):
        self.km = KeyManager()
        self.content = None
        self.data = None
        self.status = ''
        self.import_log = []
        self.modules = []

    def read_package(self, filename):
        """Read the file content.

        It is normally an armored PGP file with signature.
        """
        if isinstance(filename, (str, bytes, os.PathLike)):
            try:
                with open(filename, "r") as fdesc:
                    self.content = fdesc.read()
                    fdesc.close()
            except IOError as error:
                log.error("File impossible to read. %s", error)
                self.status = _("File impossible to read. See detailled log.")
                return False
            except UnicodeDecodeError as error:
                log.error("File impossible to read (not an ASCII file). %s", error)
                self.status = _("File impossible to read. See detailled log.")
                return False
        elif isinstance(filename, io.TextIOWrapper):
            try:
                self.content = filename.read()
            except UnicodeDecodeError as error:
                log.error("File impossible to read (not an ASCII file). %s", error)
                self.status = _("File impossible to read. See detailled log.")
                return False
        else:
            log.error("Filename instance not compatible! What is this?!!")
            self.status = _("File impossible to read. See detailled log.")
            return False
        return True

    def check_signature(self):
        res = self.km.check_signature(self.content)
        if not res:
            log.error("Error during signature check: %s", self.km.status)
            self.status = _("Signature not validated. See detailled log.")
            return False

        # Save the result in the instance
        self.data = res
        return True

    def check_conformity(self):
        """Check that the package has a 'package.conf' file and that it is readable."""
        # Check if the `self.data` data is a real tar file
        res = check_tarfile(self.data)
        if not res:
            self.status = _("Signed data is not a valid Tar file. Check logs.")
            return False

        self.archive = res

        # Check the manifest checksums
        res = check_integrity(self.archive)
        if not res:
            self.status = _("Integrity check failed. Check logs.")
            return False

        # Check the configuration file is present
        if "package.yaml" not in self.archive.getnames():
            self.status = _("Configuration not found.")
            return False

        # Getting information from the package.conf file
        conf = self.archive.extractfile('package.yaml').read()
        self.conf = load_config(conf, "package.json")

        if not self.conf:
            self.status = _("Configuration file incorrect. ")
            return False

        self.import_log.append({'name': _('Package Author'), 'value': self.conf['info']['author']})
        self.import_log.append({'name': _('Package Version'), 'value': self.conf['info']['version']})
        self.import_log.append({'name': _('Package Date'), 'value': self.conf['info']['date']})

        # Save the list of the packages and check if the related django application exists.
        self.modules = self.conf['modules']
        for module_name in self.modules.keys():
            module = "pharmaship.{0}".format(module_name)
            if module not in settings.INSTALLED_APPS:
                log.error("Module not installed: %s", module)
                self.status = _("A module to update is not installed. Check logs for details.")
                return False
        return True

    def deploy(self):
        """Propagate the import to concerned modules."""
        for module in self.modules:

            import_class = load_module(module)
            if not import_class:
                self.status = _("Module import error. See detailed log.")
                return False

            data_import = import_class(
                tar=self.archive,
                conf=self.conf,
                key=self.km.key)

            if not (hasattr(data_import, "update") and callable(data_import.update)):
                log.error("Module %s has no DataImport.update method.", module)
                self.status = _("Target module has no update method. See detailed log.")
                return False

            step_result = data_import.update()
            if not step_result:
                msg = _("Import of module {0} failed. See detailed logs.").format(module)
                log.error(msg)
            else:
                msg = _("Import of module {0} succeeded.").format(module)
                log.info(msg)

            self.import_log.append({'name': module, 'value': msg})

        self.status = _("Import success.")

        return True
