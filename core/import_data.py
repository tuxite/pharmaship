# -*- coding: utf-8; -*-
from django.utils.translation import ugettext as _

import tarfile
import xml.dom.minidom
import gnupg
import io
import ConfigParser
import json
import hashlib
import importlib

from django.http import HttpResponse, HttpResponseBadRequest
from django.conf import settings

from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

# TODO: Logging using Django Logging module. Then call the log content in the template.
def extract_manifest(manifest_descriptor):
    """Extracts the MANIFEST information and puts it into a list of dict."""
    data = manifest_descriptor.readlines()
    result = []
    for item in data:
        f = {}
        f['hash'], f['filename'] = item.strip().split("  ")
        result.append(f)

    return result

def remove_xml_pk(xml_string):
    """Removes the PK attributes to the serialized objects. XML Version.

    This allows to import different alllowances with for instance the
    same molecules without generating conflicts of primary key.
    """
    dom = xml.dom.minidom.parseString(xml_string)
    for node in dom.getElementsByTagName('object'):
        if node.hasAttribute("pk"):
            node.removeAttribute("pk")
    return dom.toxml("utf-8")

def remove_yaml_pk(yaml_string):
    """Removes the PK attributes to the serialized objects. YAML Version.

    This allows to import different alllowances with for instance the
    same molecules without generating conflicts of primary key.
    """
    data = load(yaml_string, Loader=Loader)
    for item in data:
        try:
            del item['pk']
        except KeyError:
            pass

    output = dump(data, Dumper=Dumper)
    return output

class BaseImport:
    """Class used to import a data file in Onboard Assistant."""
    def __init__(self, import_file):
        """Reads the file and creates a gnupg.GPG instance."""
        self.signed = import_file.read()
        self.gpg = gnupg.GPG(gnupghome=settings.KEYRING)
        self.clear_tar = None
        self.error = ''
        self.log = []
        self.core_log = []

    def check_signature(self):
        # Verifying the signature
        verified = self.gpg.verify(self.signed)

        # Check first is the signature is valid
        if not verified:
            self.error = _("No signature found.")
            return False

        # Then check that it is in the keyring
        key = None
        for k in self.gpg.list_keys():
            if k['keyid'] == verified.key_id:
                key = k
                break
            
            # Also check in the subkeys
            for sk in k['subkeys']:
                if sk[0] == verified.key_id:
                    key = k
                    break
                
        if not key:
            self.error = _("Signature not in the keyring.")
            return False

        # Decrypt the file
        self.clear_tar = self.gpg.decrypt(self.signed).data

        # LOG
        self.core_log.append({'name': _('Package Signature'), 'value': u"Verified, {0} [{1}]".format(verified.username, verified.key_id[-8:])})
        return True

    def check_integrity(self, tar):
        """Opens the presumed archives and checks that some files are inside."""

        # Open the MANIFEST
        self.manifest = extract_manifest(tar.extractfile("MANIFEST"))
        # Basic check of length
        # TODO: Raise an error when a file (not a directory) in the archive is not in the MANIFEST.
        #~ print "MANIFEST", len(self.manifest), "TAR", len(tar.getmembers()), tar.getmembers()
        # Check the MD5sum
        for item in self.manifest:
            m = hashlib.md5()
            m.update(tar.extractfile(item['filename']).read())
            tarfile_hash =  m.hexdigest()
            if tarfile_hash != item['hash']:
                self.error = _("File corrupted: ") + item['filename']
                return False

        return True

    def check_conformity(self, tar):
        """Checks that the package has a 'package.conf' file and that it is readable."""
        try:
            conf = tar.extractfile('package.conf')
        except KeyError as e:
            self.error = _("Configuration not found. Details: ") + str(e)
            return False

        # Getting information from the package.conf file
        self.conf = ConfigParser.ConfigParser()

        try:
            self.conf.readfp(conf)
            self.core_log.append({'name': _('Package Author'), 'value': self.conf.get('info', 'author')})
            self.core_log.append({'name': _('Package Version'), 'value': self.conf.get('info', 'version')})
            self.core_log.append({'name': _('Package Date'), 'value': self.conf.get('info', 'date')})

        except ConfigParser.NoSectionError as e:
            self.error = _("Configuration file incorrect. ") + str(e)
            return False
        except ConfigParser.NoOptionError as e:
            self.error = _("Configuration file incorrect. ") + str(e)
            return False

        # Save the list of the packages and check if the related OA module exists.
        self.modules = self.conf.sections()
        self.modules.remove('info')
        for module in self.modules:
            if module not in settings.INSTALLED_APPS:
                self.error = _("Configuration file incorrect. ") + _("This module is not installed: ") + module
                return False
        return True

    def launch(self):
        """Launches the importation."""
#        # 1. Update the keyring
#        self.update_keyring()
#        self.core_log.append({'name': _("Trusted Keys"), 'value': _("Database updated")})
        # 2. Check the signature
        if not self.check_signature():
            self.core_log.append({'name': _("Signature Error"), 'value': self.error, 'type': 'error'})
            self.log.append({'name': 'core', 'value': self.core_log})
            data = json.dumps({'error': _('Something went wrong!'), 'log': self.log})
            return HttpResponseBadRequest(data, content_type = "application/json")
        # 3. Open the tarfile
        try:
            with tarfile.open(fileobj=io.BytesIO(self.clear_tar), mode="r") as tar:
                # 4. Verify the integrity of the archive
                if not self.check_integrity(tar):
                    self.core_log.append({'name': _("Integrity Error"), 'value': self.error, 'type': 'error'})
                    self.log.append({'name': 'core', 'value': self.core_log})
                    data = json.dumps({'error': _('Something went wrong!'), 'log': self.log})
                    return HttpResponseBadRequest(data, content_type = "application/json")
                # 5. Verify the conformity of the archive
                if not self.check_conformity(tar):
                    self.core_log.append({'name': _("Conformity Error"), 'value': self.error, 'type': 'error'})
                    self.log.append({'name': 'core', 'value': self.core_log})
                    data = json.dumps({'error': _('Something went wrong!'), 'log': self.log})
                    return HttpResponseBadRequest(data, content_type = "application/json")
                # Add the core module log to the log
                self.log.append({'name': 'core', 'value': self.core_log})
                # 6. Call the related module import function
                for module in self.modules:
                    try:
                        module_pkg = importlib.import_module(module + ".import_data")
                        module_fn = module_pkg.DataImport(tar)
                        if not module_fn.launch():
                            data = json.dumps({'error': _('Something went wrong!'), 'log': {module: module_fn.error}})
                            return HttpResponseBadRequest(data, content_type = "application/json")
                        self.log.append({'name': module, 'value': module_fn.data})

                    except ImportError:
                        self.error = _("Module %s has no import function.") % module
                        self.log.append({'core': [{'name': _("Import Error"), 'value': self.error, 'type': 'error'}]})
                        data = json.dumps({'error': _('Something went wrong!'), 'log': self.log})
                        return HttpResponseBadRequest(data, content_type = "application/json")

        except tarfile.ReadError as e:
            self.error = _("Not a valid archive: ") + str(e)
            self.core_log.append({'name': _("Archive Error"), 'value': self.error, 'type': 'error'})
            self.log.append({'name': 'core', 'value': self.core_log})
            data = json.dumps({'error': _('Something went wrong!'), 'log': self.log})
            return HttpResponseBadRequest(data, content_type = "application/json")


        # 7. Return
        data = json.dumps({'success': _('Data successfully imported'), 'log': self.log})
        return HttpResponse(data, content_type = "application/json")

