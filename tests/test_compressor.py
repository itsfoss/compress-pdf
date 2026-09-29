# SPDX-License-Identifier: GPL-3.0-or-later
import os
import subprocess

import pytest
from gi.repository import GLib

from compress_pdf.compressor import (
    CompressionJob, ProgressParser, Status, build_args, clean_workdir, is_pdf,
)
from compress_pdf.errors import ErrorKind
from compress_pdf.levels import LEVELS, get_level

from conftest import GS


def run(job, cancel_on_progress=False, timeout=120):
    loop = GLib.MainLoop()
    progress, results = [], []

    def on_progress(done, total):
        progress.append((done, total))
        if cancel_on_progress:
            job.cancel()

    def on_finished(result):
        results.append(result)
        loop.quit()

    job.start(on_progress, on_finished)
    GLib.timeout_add_seconds(timeout, loop.quit)
    loop.run()
    assert results, 'job did not finish in time'
    return results[0], progress


def page_count(path):
    out = subprocess.run(
        [GS, '-q', '-dNODISPLAY', '-dNOSAFER', '-c',
         f'({path}) (r) file runpdfbegin pdfpagecount = quit'],
        capture_output=True, text=True, check=True,
    )
    return int(out.stdout.strip())


# --- pure helpers -----------------------------------------------------------

def test_build_args_per_level():
    for level in LEVELS:
        args = build_args('gs', '/in.pdf', '/tmp/out.pdf', level)
        assert f'-dColorImageResolution={level.image_dpi}' in args
        assert f'-dMonoImageResolution={level.mono_dpi}' in args
        assert f'/QFactor {level.jpeg_qfactor}' in args[args.index('-c') + 1]
        assert args[-2:] == ['-f', '/in.pdf']
        assert '-dSAFER' in args
        assert '-dPassThroughJPXImages=false' in args


def test_build_args_escapes_percent():
    args = build_args('gs', 'in.pdf', '/tmp/100%.pdf', get_level('balanced'))
    assert '-sOutputFile=/tmp/100%%.pdf' in args


def test_progress_parser():
    p = ProgressParser()
    assert p.total is None
    assert p.feed('GPL Ghostscript 10.06.0 (2025-09-09)') is False
    assert p.feed('Processing pages 1 through 47.')
    assert (p.done, p.total) == (0, 47)
    assert p.feed('Page 1')
    assert p.feed('Page 12')
    assert (p.done, p.total) == (12, 47)


def test_is_pdf(tmp_path, samples):
    assert is_pdf(samples['text'])
    assert not is_pdf(samples['fake'])
    assert not is_pdf(str(tmp_path / 'missing.pdf'))


def test_clean_workdir(tmp_path):
    (tmp_path / 'left.pdf').write_bytes(b'x')
    (tmp_path / 'keep.txt').write_bytes(b'x')
    clean_workdir(str(tmp_path))
    assert sorted(os.listdir(tmp_path)) == ['keep.txt']


# --- real Ghostscript runs --------------------------------------------------

@pytest.mark.parametrize('level_id', [level.id for level in LEVELS])
def test_compresses_image_pdf(samples, tmp_path, level_id):
    job = CompressionJob(samples['image'], get_level(level_id), workdir=str(tmp_path))
    result, progress = run(job)

    assert result.status is Status.COMPRESSED, result.details
    assert result.output_size < result.input_size
    assert os.path.getsize(result.output_path) == result.output_size
    assert page_count(result.output_path) == 3
    assert progress[0] == (0, 3)
    assert progress[-1] == (3, 3)


def test_levels_get_smaller(samples, tmp_path):
    sizes = []
    for level in LEVELS:
        result, _ = run(CompressionJob(samples['image'], level, workdir=str(tmp_path)))
        sizes.append(result.output_size)
    assert sizes == sorted(sizes, reverse=True), sizes


def test_text_only_is_not_smaller(samples, tmp_path):
    result, _ = run(CompressionJob(samples['text'], get_level('balanced'), workdir=str(tmp_path)))
    assert result.status is Status.NOT_SMALLER
    assert result.output_path is None
    assert os.listdir(tmp_path) == []


def test_password_protected(samples, tmp_path):
    result, _ = run(CompressionJob(samples['locked'], get_level('balanced'), workdir=str(tmp_path)))
    assert result.status is Status.FAILED
    assert result.error is ErrorKind.PASSWORD
    assert os.listdir(tmp_path) == []


def test_not_a_pdf_never_reaches_ghostscript(samples, tmp_path):
    result, progress = run(CompressionJob(samples['fake'], get_level('balanced'), gs='/nonexistent/gs'))
    assert result.error is ErrorKind.NOT_PDF
    assert progress == []


def test_missing_file(tmp_path):
    result, _ = run(CompressionJob(str(tmp_path / 'gone.pdf'), get_level('balanced')))
    assert result.error is ErrorKind.READ_FAILED


def test_ghostscript_missing(samples, tmp_path):
    job = CompressionJob(samples['image'], get_level('balanced'), gs='/nonexistent/gs', workdir=str(tmp_path))
    result, _ = run(job)
    assert result.error is ErrorKind.GS_MISSING


def test_odd_file_name(samples, tmp_path):
    result, _ = run(CompressionJob(samples['odd'], get_level('balanced'), workdir=str(tmp_path)))
    assert result.status is Status.COMPRESSED, result.details


def test_cancel(samples, tmp_path):
    job = CompressionJob(samples['image'], get_level('balanced'), workdir=str(tmp_path))
    result, _ = run(job, cancel_on_progress=True)
    assert result.status is Status.CANCELLED
    assert os.listdir(tmp_path) == []
