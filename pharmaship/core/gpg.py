# -*- coding: utf-8; -*-
"""Utilities for GPG signature handling."""
import gnupg

from django.utils.translation import ugettext as _

from django.conf import settings

from pharmaship.core.utils import log


class KeyManager:
    """Class used to manage PGP keys used for external data import."""

    def __init__(self):
        """Create a GPG context and select the keyring."""
        self.gpg = gnupg.GPG(gnupghome=settings.KEYRING_PATH)
        self.status = ""

    def add_key(self, import_file):
        """Add a key to the keyring.

        :param: import_file: File object containing the key data.
        :type: import_file: file-like object"""
        key_data = import_file.read()
        r = self.gpg.import_keys(key_data)

        for item in r.results:
            if 'ok' not in item.keys():
                log.error("Signature error: %s", item["text"])
                self.status = _('Something went wrong! See detailed logs.')
                return False

        if r.imported == 0:
            log.info("Key already added.")
            self.status = _('Key already added')
        else:
            key = self.get_key(r.fingerprints[0])
            item = {"name": key['uids'][0], "fingerprint": key['fingerprint']}
            log.debug(item)
            self.status = _('Key successfully added')
        return True

    def key_list(self):
        """List trusted keys present in the keyring."""
        result = []
        for key in self.gpg.list_keys():
            result.append({
                "name": key['uids'][0],
                "fingerprint": key['fingerprint']
                })

        return result

    def get_key(self, fingerprint):
        """Return a key of the keyring from its fingerprint."""
        for item in self.gpg.list_keys():
            if item['fingerprint'] == fingerprint:
                return item
        return None

    def delete_key(self, fingerprint):
        """Delete key from the keyring."""
        try:
            r = self.gpg.delete_keys(fingerprint)
            if r.status != 'ok':
                raise ValueError(r.status)

        except ValueError as e:
            log.error("Key not found: %s", e)
            self.status = _('Key not found!')
            return False

        self.status = _('Key removed')
        return True

    def check_signature(self, signed_data):
        """Check signed data has a valid known signature."""
        # Verifying the signature
        verified = self.gpg.verify(signed_data)

        # Check first is the signature is valid
        if not verified:
            self.status = _("No signature found.")
            return False

        # Then check that it is in the keyring
        self.key = None
        for k in self.gpg.list_keys():
            if k['keyid'] == verified.key_id:
                self.key = k
                break

            # Also check in the subkeys
            for sk in k['subkeys']:
                if sk[0] == verified.key_id:
                    self.key = k
                    break

        if not self.key:
            self.status = _("Signature not in the keyring.")
            return False

        # Decrypt the file
        log.info(
            "Package signature correct and verified (%s, %s)",
            verified.username,
            verified.key_id[-8:]
            )
        return self.gpg.decrypt(signed_data).data
