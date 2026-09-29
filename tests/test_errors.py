# SPDX-License-Identifier: GPL-3.0-or-later
from compress_pdf.errors import ErrorKind, classify, message, was_repaired


def test_classify_password():
    out = "   **** This file requires a password for access.\n   **** Error: Couldn't initialise file."
    assert classify(out) is ErrorKind.PASSWORD


def test_classify_damaged():
    assert classify("**** Error: Couldn't initialise file.") is ErrorKind.DAMAGED


def test_classify_disk_full():
    assert classify('Last OS error: No space left on device') is ErrorKind.WRITE_FAILED


def test_classify_unknown():
    assert classify('something odd') is ErrorKind.UNKNOWN


def test_repaired():
    assert was_repaired('The following errors were encountered at least once\n\txref table was repaired')
    assert not was_repaired('Processing pages 1 through 1.\nPage 1')


def test_every_kind_has_a_message():
    for kind in ErrorKind:
        assert message(kind)
