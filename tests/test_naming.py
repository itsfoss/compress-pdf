# SPDX-License-Identifier: GPL-3.0-or-later
from compress_pdf.naming import output_name, unique_path


def test_output_name():
    assert output_name('report.pdf') == 'report-compressed.pdf'
    assert output_name('/home/u/Scan.PDF') == 'Scan-compressed.pdf'
    assert output_name('my.file.v2.pdf') == 'my.file.v2-compressed.pdf'
    assert output_name('noext') == 'noext-compressed.pdf'


def test_unique_path_free():
    assert unique_path('/out', 'a.pdf', exists=lambda p: False) == '/out/a.pdf'


def test_unique_path_counts_up():
    existing = {'/out/a.pdf', '/out/a-2.pdf'}
    assert unique_path('/out', 'a.pdf', exists=existing.__contains__) == '/out/a-3.pdf'


def test_unique_path_respects_batch():
    taken = {'/out/a.pdf'}
    assert unique_path('/out', 'a.pdf', exists=lambda p: False, taken=taken) == '/out/a-2.pdf'
