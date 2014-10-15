# -*- coding: utf-8; -*-
from django.utils.translation import ugettext as _
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render_to_response

from django.conf import settings

import gnupg
import json

class KeyManager:
    """Class used to manager PGP keys used for external data import."""

    def __init__(self):
        """Creates a GPG context and select the keyring."""
        self.gpg = gnupg.GPG(gnupghome=settings.KEYRING)
        self.error = ''
        self.log = []
        self.core_log = []

    def add_key(self, import_file):
        """Adds a key to the keyring."""
        key_data = import_file.read()
        r = self.gpg.import_keys(key_data)

        for item in r.results:
            if not 'ok' in item.keys():
                self.error = _("No signature imported.") + " " + str(item['text'])
                self.core_log.append({'name': _("Signature Error"), 'value': self.error, 'type': 'error'})
                self.log.append({'name': 'core', 'value': self.core_log})
                data = json.dumps({'error': _('Something went wrong!'), 'log': self.log})
                return HttpResponseBadRequest(data, content_type = "application/json")

        if r.imported == 0:
            data = json.dumps({'success': _('Key already added'),})
        else:
            key = self.get_key(r.fingerprints[0])
            item = {"name": key['uids'][0], "fingerprint": key['fingerprint']}
            content = render_to_response('settings/key.inc.html', {
                    'item': item,
                    }).content
            data = json.dumps({'success': _('Key successfully added'), 'key': content})
        return HttpResponse(data, content_type = "application/json")

    def key_list(self):
        """Lists trusted keys present in the keyring."""
        result = []
        for key in self.gpg.list_keys():
            result.append({"name": key['uids'][0], "fingerprint": key['fingerprint']})

        return result

    def get_key(self, fingerprint):
        """Returns a key of the keyring from its fingerprint."""
        for item in self.gpg.list_keys():
            if item['fingerprint'] == fingerprint:
                return item
        return None

    def delete_key(self, fingerprint):
        """Deletes key from the keyring."""
        try:
            r = self.gpg.delete_keys(fingerprint)
            if r.status != 'ok':
                raise ValueError(r.status)

        except ValueError as e:
            self.error = _("Key not found.") + str(e)
            self.core_log.append({'name': _("Signature Error"), 'value': self.error, 'type': 'error'})
            self.log.append({'name': 'core', 'value': self.core_log})
            data = json.dumps({'error': _('Something went wrong!'), 'log': self.log})
            return HttpResponseBadRequest(data, content_type = "application/json")

        data = json.dumps({'success': _('Key removed'), 'log': self.log})
        return HttpResponse(data, content_type = "application/json")