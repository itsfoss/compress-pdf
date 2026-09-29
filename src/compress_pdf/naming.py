# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 It's FOSS
"""Output file names that never overwrite an existing file."""

import os

SUFFIX = '-compressed'


def output_name(source_name):
    """report.pdf -> report-compressed.pdf"""
    stem, ext = os.path.splitext(os.path.basename(source_name))
    if ext.lower() != '.pdf':
        stem, ext = stem + ext, ''
    return f'{stem}{SUFFIX}.pdf'


def unique_path(folder, name, exists=os.path.exists, taken=()):
    """Return folder/name, or folder/name-2.pdf, -3 ... if already in use.

    `taken` holds paths already promised to other files in the same batch.
    """
    stem, ext = os.path.splitext(name)
    candidate = os.path.join(folder, name)
    n = 2
    while candidate in taken or exists(candidate):
        candidate = os.path.join(folder, f'{stem}-{n}{ext}')
        n += 1
    return candidate
