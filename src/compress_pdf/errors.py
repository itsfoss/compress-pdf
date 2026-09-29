# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 It's FOSS
"""Turn Ghostscript output into something a person can act on."""

import enum

from .levels import N_


class ErrorKind(enum.Enum):
    GS_MISSING = 'gs-missing'
    NOT_PDF = 'not-pdf'
    PASSWORD = 'password'
    DAMAGED = 'damaged'
    NO_PAGES = 'no-pages'
    READ_FAILED = 'read-failed'
    WRITE_FAILED = 'write-failed'
    UNKNOWN = 'unknown'


MESSAGES = {
    ErrorKind.GS_MISSING: N_('Ghostscript is not installed. Install the “ghostscript” package and try again.'),
    ErrorKind.NOT_PDF: N_('This is not a PDF file.'),
    ErrorKind.PASSWORD: N_('This PDF is password protected.'),
    ErrorKind.DAMAGED: N_('This PDF is damaged and could not be read.'),
    ErrorKind.NO_PAGES: N_('This PDF has no pages.'),
    ErrorKind.READ_FAILED: N_('The file could not be read.'),
    ErrorKind.WRITE_FAILED: N_('The compressed file could not be written. Check that there is enough free space.'),
    ErrorKind.UNKNOWN: N_('Ghostscript could not compress this file.'),
}

# Checked in order against Ghostscript's combined output, lower-cased.
_PATTERNS = (
    ('requires a password', ErrorKind.PASSWORD),
    ('password did not work', ErrorKind.PASSWORD),
    ('undefinedfilename', ErrorKind.READ_FAILED),
    ('no space left on device', ErrorKind.WRITE_FAILED),
    ('could not open the file', ErrorKind.WRITE_FAILED),
    ('ioerror', ErrorKind.WRITE_FAILED),
    ("couldn't initialise file", ErrorKind.DAMAGED),
    ('unrecoverable error', ErrorKind.DAMAGED),
)

# Ghostscript prints this when it repaired a broken file and carried on.
_REPAIRED = ('was repaired', 'errors were encountered')


def classify(output):
    """Return the ErrorKind that best explains a failed run."""
    text = output.lower()
    for needle, kind in _PATTERNS:
        if needle in text:
            return kind
    return ErrorKind.UNKNOWN


def was_repaired(output):
    text = output.lower()
    return any(needle in text for needle in _REPAIRED)


def message(kind):
    return _(MESSAGES[kind])
