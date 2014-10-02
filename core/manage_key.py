from django.utils.translation import ugettext as _
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render_to_response

from django.conf import settings

import gpgme, os, json

class KeyManager:
    """Class used to manager PGP keys used for external data import."""
    
    def __init__(self):
        """Creates a GPG context and select the keyring."""
        self.gpg = gpgme.Context()
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
        
    def add_key(self, import_file):
        """Adds a key to the keyring."""
        try:
            r = self.gpg.import_(import_file)
            if not r.imports:
                raise gpgme.GpgmeError("Nothing to import")
                
        except gpgme.GpgmeError as e:
            self.error = _("No signature found.") + " " + str(e)            
            self.core_log.append({'name': _("Signature Error"), 'value': self.error, 'type': 'error'})
            self.log.append({'name': 'core', 'value': self.core_log})
            data = json.dumps({'error': _('Something went wrong!'), 'log': self.log})
            return HttpResponseBadRequest(data, content_type = "application/json")
        
        if r.imported == 0:
            data = json.dumps({'success': _('Key already added'),})
        else:
            key = self.gpg.get_key(r.imports[0][0][-8:])
            item = {"name": key.uids[0].uid, "id": key.subkeys[0].keyid[-8:]}
            content = render_to_response('settings/key.inc.html', {
                    'item': item,
                    }).content 
            data = json.dumps({'success': _('Key successfully added'), 'key': content})
        return HttpResponse(data, content_type = "application/json")
        
    def key_list(self):
        """Lists trusted keys present in the keyring."""
        result = []        
        for key in self.gpg.keylist():
            result.append({"name": key.uids[0].uid, "id": key.subkeys[0].keyid[-8:]}) #NOTE: Is there a better method to get the key id?
        
        return result
        
    def delete_key(self, key_id):
        """Deletes key from the keyring."""
        try:
            key = self.gpg.get_key(key_id)
            
        except gpgme.GpgmeError as e:
            self.error = _("Key not found.") + str(e)
            self.core_log.append({'name': _("Signature Error"), 'value': self.error, 'type': 'error'})
            self.log.append({'name': 'core', 'value': self.core_log})            
            data = json.dumps({'error': _('Something went wrong!'), 'log': self.log})
            return HttpResponseBadRequest(data, content_type = "application/json")
        
        self.gpg.delete(key)
        data = json.dumps({'success': _('Key successfully removed'), 'log': self.log})
        return HttpResponse(data, content_type = "application/json")