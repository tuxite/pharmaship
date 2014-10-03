# -*- coding: utf-8; -*-
from django.utils.translation import ugettext as _

import tarfile
import xml.dom.minidom
import gpgme, os
import io, ConfigParser
import json
import hashlib
import importlib

from django.http import HttpResponse, HttpResponseBadRequest
from django.conf import settings

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
    
def remove_pk(xml_string):
    """Removes the PK attributes to the serialized objects.

    This allows to import different alllowances with for instance the
    same molecules without generating conflicts of primary key.
    """
    dom = xml.dom.minidom.parseString(xml_string)
    for node in dom.getElementsByTagName('object'):
        if node.hasAttribute("pk"):
            node.removeAttribute("pk")
    return dom.toxml("utf-8")


class BaseImport:
    """Class used to import a data file in Onboard Assistant."""
    def __init__(self, import_file):
        """Saves the file and create a GPG context."""
        self.signed = import_file
        self.gpg = gpgme.Context()
        self.clear_tar = io.BytesIO()
        self.error = ''
        self.log = []
        self.core_log = []
        
        # Select the keyring
        if settings.KEYRING:
            os.environ['GNUPGHOME'] = settings.KEYRING
        # Then, check the keyring
        self.check_keyring()
        
    def check_keyring(self):
        """Checks if the keyring exists or creates a folder."""
        if not os.path.exists(settings.KEYRING):
            os.mkdir(settings.KEYRING)
            
    def check_signature(self):
        # Verifying the signature
        try:
            verified = self.gpg.verify(self.signed, None, self.clear_tar)
        except gpgme.GpgmeError as e:
            self.error = _("No signature found.") + str(e)
            return False
        if not verified:
            self.error = _("No signature found.")
            return False

        # Signature data
        if verified[0].status:
            # If it is different of 0 (GPG_ERR_NO_ERROR), abort the import process
            # In case of key not trusted, this error is raised.
            self.error = _("Signature not valid. Error:") + " " + verified[0].status[-1]
            return False

        fpr = verified[0].fpr
        key_id = fpr[-8:]
        
        try:
            key = self.gpg.get_key(key_id)
        except gpgme.GpgmeError as e:
            self.error = _("Signature not valid. Error:") + " " + str(e)
            return False
            
        # LOG
        self.core_log.append({'name': _('Package Signature'), 'value': u"Verified, {0} [{1}]".format(key.uids[0].uid, key_id)})
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
            with tarfile.open(fileobj=io.BytesIO(self.clear_tar.getvalue()), mode="r") as tar:
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
        
