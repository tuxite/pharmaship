#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Pharmaship Django makemessages customized command."""
import os
from django.core.management.base import CommandError
from django.core.management.commands.makemessages import Command as MakeMessagesCommand
from django.core.management.commands.makemessages import normalize_eols

from django.core.management.utils import popen_wrapper


STATUS_OK = 0

class Command(MakeMessagesCommand):
    files_root = 'pharmaship/'

    def build_potfiles(self):
        """
        Build pot files and apply msguniq to them.
        """
        file_list = self.find_files(self.files_root)
        self.remove_potfiles()
        self.process_files(file_list)
        potfiles = []
        for path in self.locale_paths:
            potfile = os.path.join(path, '%s.pot' % self.domain)
            if not os.path.exists(potfile):
                continue
            args = ['msguniq'] + self.msguniq_options + [potfile]
            msgs, errors, status = popen_wrapper(args)
            if errors:
                if status != STATUS_OK:
                    raise CommandError(
                        "errors happened while running msguniq\n%s" % errors)
                elif self.verbosity > 0:
                    self.stdout.write(errors)
            msgs = normalize_eols(msgs)
            with open(potfile, 'w', encoding='utf-8') as fp:
                fp.write(msgs)
            potfiles.append(potfile)
        return potfiles
