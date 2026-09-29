# SPDX-License-Identifier: GPL-3.0-or-later
import os
import shutil

from gi.repository import GLib

from compress_pdf.batch import Batch
from compress_pdf.compressor import Status
from compress_pdf.levels import get_level


def run(batch, cancel_after_first=False):
    loop = GLib.MainLoop()
    events = []

    def finished(index, result, saved):
        events.append(('finished', index, result.status, saved))
        if cancel_after_first:
            batch.cancel()

    def all_done(cancelled):
        events.append(('all-done', cancelled))
        loop.quit()

    batch.start(
        lambda i: events.append(('started', i)),
        lambda i, done, total: None,
        finished,
        all_done,
    )
    GLib.timeout_add_seconds(120, loop.quit)
    loop.run()
    return events


def test_folder_mode_names_and_no_overwrite(samples, tmp_path):
    a = tmp_path / 'a'
    b = tmp_path / 'b'
    out = tmp_path / 'out'
    for d in (a, b, out):
        d.mkdir()
    shutil.copy(samples['image'], a / 'scan.pdf')
    shutil.copy(samples['image'], b / 'scan.pdf')
    (out / 'scan-compressed.pdf').write_bytes(b'keep me')

    batch = Batch([str(a / 'scan.pdf'), str(b / 'scan.pdf'), samples['text']],
                  get_level('balanced'), str(out), single=False, workdir=str(tmp_path / 'work'))
    events = run(batch)

    saved = [e[3] for e in events if e[0] == 'finished']
    assert saved[0] == str(out / 'scan-compressed-2.pdf')
    assert saved[1] == str(out / 'scan-compressed-3.pdf')
    assert saved[2] is None  # text-only file was not smaller
    assert batch.results[2].status is Status.NOT_SMALLER
    assert (out / 'scan-compressed.pdf').read_bytes() == b'keep me'
    assert events[-1] == ('all-done', False)
    assert os.listdir(tmp_path / 'work') == []


def test_single_mode_writes_chosen_file(samples, tmp_path):
    target = tmp_path / 'chosen name.pdf'
    target.write_bytes(b'old')  # the save dialog already confirmed overwriting
    batch = Batch([samples['image']], get_level('small'), str(target), single=True,
                  workdir=str(tmp_path / 'work'))
    events = run(batch)

    assert events[-2] == ('finished', 0, Status.COMPRESSED, str(target))
    assert target.stat().st_size == batch.results[0].output_size


def test_cancel_stops_the_queue(samples, tmp_path):
    out = tmp_path / 'out'
    out.mkdir()
    batch = Batch([samples['image'], samples['image']], get_level('balanced'), str(out),
                  single=False, workdir=str(tmp_path / 'work'))
    events = run(batch, cancel_after_first=True)

    assert [e for e in events if e[0] == 'started'] == [('started', 0)]
    assert events[-1] == ('all-done', True)
    assert len(os.listdir(out)) == 1


def test_unwritable_destination(samples, tmp_path):
    batch = Batch([samples['image']], get_level('balanced'), str(tmp_path / 'missing' / 'dir'),
                  single=False, workdir=str(tmp_path / 'work'))
    run(batch)
    assert batch.results[0].status is Status.FAILED
    assert os.listdir(tmp_path / 'work') == []
