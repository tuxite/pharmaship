#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import re

from django.core.management.base import BaseCommand

from pharmaship.core.gpg import KeyManager
from pharmaship.core.utils import log


class Command(BaseCommand):
    help = "GPG Key management for package import in Pharmaship."

    def add_arguments(self, parser) -> None:
        subparsers = parser.add_subparsers(help='Action on keyring.')

        parser_list = subparsers.add_parser('list', help='List stored keys in the keyring.')
        parser_list.set_defaults(func=self.list)

        parser_add = subparsers.add_parser('add', help='Add a key from file to the keyring.')
        parser_add.add_argument("file", help='Key filename.', type=argparse.FileType('r'))
        parser_add.set_defaults(func=self.add)

        parser_delete = subparsers.add_parser('delete', help='Delete a key from the keyring.')
        parser_delete.add_argument("fingerprint", help='Key fingerprint.')
        parser_delete.set_defaults(func=self.delete)

        parser_get = subparsers.add_parser('get', help='Get a key from the keyring.')
        parser_get.add_argument("fingerprint", help='Key fingerprint.')
        parser_get.set_defaults(func=self.get)

    def handle(self, *args, **options):
        if "fingerprint" in options:
            regex = re.search(r"^[0-9a-fA-F]{40}$", options["fingerprint"])
            if not regex:
                log.error("Fingerprint not correct.")
                return False

        if "func" in options:
            options['func'](options)

    def list(self, args):
        log.info("Listing keys")
        km = KeyManager()
        res = km.key_list()

        log.info(res)

    def add(self, args):
        log.info("Adding key from file.")

        km = KeyManager()
        res = km.add_key(args["file"])
        log.info(res)

    def delete(self, args):
        log.info("Deleting keys")

        km = KeyManager()
        res = km.delete_key(args["fingerprint"])
        log.info(res)

    def get(self, args):
        log.info("Getting keys")

        km = KeyManager()
        res = km.get_key(args["fingerprint"])
        log.info(res)
