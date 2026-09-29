# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 It's FOSS
"""Run Ghostscript on one PDF without blocking the main loop.

No GTK in here, so it can be tested without a display.
"""

import collections
import enum
import os
import re
import uuid
from dataclasses import dataclass

from gi.repository import Gio, GLib

from . import errors
from .errors import ErrorKind

# A result must be at least this much smaller than the original to be kept.
MIN_SAVING = 0.05

_PAGES_RE = re.compile(r'^Processing pages (\d+) through (\d+)\.')
_PAGE_RE = re.compile(r'^Page (\d+)$')
_OUTPUT_TAIL = 60


class Status(enum.Enum):
    COMPRESSED = 'compressed'
    NOT_SMALLER = 'not-smaller'
    FAILED = 'failed'
    CANCELLED = 'cancelled'


@dataclass
class Result:
    status: Status
    input_size: int = 0
    output_size: int = 0
    output_path: str | None = None
    error: ErrorKind | None = None
    details: str = ''
    repaired: bool = False

    @property
    def saving(self):
        """Fraction saved, e.g. 0.82 for 82% smaller."""
        if not self.input_size or not self.output_size:
            return 0.0
        return 1 - self.output_size / self.input_size


def find_ghostscript():
    return GLib.find_program_in_path('gs')


def is_pdf(path):
    """True if the file starts with a PDF header.

    Ghostscript runs anything else as PostScript, which we never want.
    The spec allows junk before the header, so look at the first 1 KiB.
    """
    try:
        with open(path, 'rb') as f:
            return b'%PDF-' in f.read(1024)
    except OSError:
        return False


def _distiller_params(qfactor):
    jpeg = f'<< /QFactor {qfactor} /Blend 1 /HSamples [2 1 1 2] /VSamples [2 1 1 2] >>'
    dicts = ' '.join(
        f'/{name} {jpeg}'
        for name in ('ColorImageDict', 'ColorACSImageDict', 'GrayImageDict', 'GrayACSImageDict')
    )
    return f'<< {dicts} >> setdistillerparams'


def build_args(gs, source, output, level):
    """Command line for compressing `source` into `output` at `level`."""
    return [
        gs,
        '-dSAFER', '-dBATCH', '-dNOPAUSE',
        '-sDEVICE=pdfwrite',
        '-dCompatibilityLevel=1.5',
        '-dAutoRotatePages=/None',
        '-dDetectDuplicateImages=true',
        '-dCompressFonts=true',
        '-dSubsetFonts=true',
        '-dPassThroughJPEGImages=false',
        '-dPassThroughJPXImages=false',
        '-dDownsampleColorImages=true',
        '-dDownsampleGrayImages=true',
        '-dDownsampleMonoImages=true',
        '-dColorImageDownsampleType=/Bicubic',
        '-dGrayImageDownsampleType=/Bicubic',
        '-dColorImageDownsampleThreshold=1.0',
        '-dGrayImageDownsampleThreshold=1.0',
        '-dMonoImageDownsampleThreshold=1.0',
        f'-dColorImageResolution={level.image_dpi}',
        f'-dGrayImageResolution={level.image_dpi}',
        f'-dMonoImageResolution={level.mono_dpi}',
        # Ghostscript expands %d in output names; escape any literal %.
        '-sOutputFile=' + output.replace('%', '%%'),
        '-c', _distiller_params(level.jpeg_qfactor),
        '-f', source,
    ]


class ProgressParser:
    """Reads Ghostscript's stdout line by line and tracks the page count."""

    def __init__(self):
        self.first = None
        self.last = None
        self.page = 0

    @property
    def total(self):
        if self.first is None:
            return None
        return max(self.last - self.first + 1, 0)

    @property
    def done(self):
        """Pages finished so far, counted from 0."""
        if self.first is None or not self.page:
            return 0
        return self.page - self.first + 1

    def feed(self, line):
        """Return True if the line changed the progress."""
        if m := _PAGES_RE.match(line):
            self.first, self.last = int(m[1]), int(m[2])
            return True
        if m := _PAGE_RE.match(line):
            self.page = int(m[1])
            return True
        return False


def default_workdir():
    return os.path.join(GLib.get_user_cache_dir(), 'compress-pdf')


def clean_workdir(workdir=None):
    """Remove temp files left behind by a crash or a killed session."""
    workdir = workdir or default_workdir()
    try:
        entries = os.listdir(workdir)
    except FileNotFoundError:
        return
    for name in entries:
        if name.endswith('.pdf'):
            try:
                os.unlink(os.path.join(workdir, name))
            except OSError:
                pass


class CompressionJob:
    """Compress one file into a temporary file.

    on_progress(done, total) and on_finished(result) are called on the
    main loop. On success the result's output_path points at the temporary
    file, which the caller moves to its final place (or deletes).
    """

    def __init__(self, source, level, gs=None, workdir=None):
        self.source = source
        self.level = level
        self.gs = gs or find_ghostscript()
        self.workdir = workdir or default_workdir()
        self.output = None
        self._cancellable = Gio.Cancellable()
        self._process = None
        self._stream = None
        self._pending = b''
        self._progress = ProgressParser()
        self._tail = collections.deque(maxlen=_OUTPUT_TAIL)
        self._on_progress = None
        self._on_finished = None
        self._finished = False
        self._staged = None

    def start(self, on_progress, on_finished):
        self._on_progress = on_progress
        self._on_finished = on_finished

        try:
            self._input_size = os.path.getsize(self.source)
        except OSError as e:
            return self._fail_later(ErrorKind.READ_FAILED, str(e))
        if not is_pdf(self.source):
            return self._fail_later(ErrorKind.NOT_PDF)
        if not self.gs:
            return self._fail_later(ErrorKind.GS_MISSING)

        try:
            os.makedirs(self.workdir, exist_ok=True)
        except OSError as e:
            return self._fail_later(ErrorKind.WRITE_FAILED, str(e))
        self.output = os.path.join(self.workdir, f'{uuid.uuid4().hex}.pdf')
        self._spawn(self.source)

    def _spawn(self, input_path):
        launcher = Gio.SubprocessLauncher.new(
            Gio.SubprocessFlags.STDOUT_PIPE | Gio.SubprocessFlags.STDERR_MERGE
        )
        launcher.setenv('LC_ALL', 'C', True)
        try:
            self._process = launcher.spawnv(build_args(self.gs, input_path, self.output, self.level))
        except GLib.Error as e:
            return self._fail_later(ErrorKind.GS_MISSING, e.message)

        self._stream = self._process.get_stdout_pipe()
        self._pending = b''
        self._progress = ProgressParser()
        self._tail.clear()
        self._read_next_chunk()

    def cancel(self):
        if self._finished:
            return
        self._cancellable.cancel()
        if self._process:
            # Where AppArmor confines gs (Ubuntu 25.10+) this is refused, so
            # _on_chunk also closes the pipe: gs then dies of SIGPIPE when it
            # reports its next page.
            self._process.force_exit()

    # Read raw chunks rather than lines: PyGObject's byte line reader returns
    # the same thing for a blank line and for end of stream, and the UTF-8
    # one fails on odd bytes (file names), which would leave gs blocked on
    # a full pipe.
    def _read_next_chunk(self):
        self._stream.read_bytes_async(
            4096, GLib.PRIORITY_DEFAULT, self._cancellable, self._on_chunk,
        )

    def _on_chunk(self, stream, res):
        try:
            chunk = stream.read_bytes_finish(res).get_data()
        except GLib.Error:
            # Cancelled, or the pipe broke; the exit status tells us which.
            chunk = b''
        if not chunk:
            if self._cancellable.is_cancelled():
                stream.close(None)
            else:
                self._handle_line(self._pending)
            self._process.wait_async(None, self._on_exit)
            return

        *lines, self._pending = (self._pending + chunk).split(b'\n')
        for line in lines:
            self._handle_line(line)
        self._read_next_chunk()

    def _handle_line(self, line):
        if not line:
            return
        text = line.decode('utf-8', errors='replace').rstrip('\r')
        self._tail.append(text)
        if self._progress.feed(text) and self._progress.total:
            self._on_progress(self._progress.done, self._progress.total)

    def _on_exit(self, process, res):
        try:
            process.wait_finish(res)
        except GLib.Error:
            pass

        if self._cancellable.is_cancelled():
            self._remove_output()
            return self._finish(Result(Status.CANCELLED, self._input_size))

        output = '\n'.join(self._tail)
        exited_ok = process.get_if_exited() and process.get_exit_status() == 0
        pages_done = self._progress.done
        try:
            output_size = os.path.getsize(self.output)
        except OSError:
            output_size = 0

        if not exited_ok or not pages_done or not output_size:
            kind = errors.classify(output)
            if kind is ErrorKind.READ_FAILED and self._staged is None and os.access(self.source, os.R_OK):
                # We can read it but gs can't: AppArmor on Ubuntu only lets gs
                # open *.pdf under $HOME, /tmp, /mnt and /media, so network
                # shares and extension-less files fail. Retry from a copy.
                return self._stage_and_retry()
            if kind is ErrorKind.UNKNOWN and exited_ok and self._progress.total == 0:
                kind = ErrorKind.NO_PAGES
            self._remove_output()
            return self._finish(Result(
                Status.FAILED, self._input_size, error=kind, details=output,
            ))

        repaired = errors.was_repaired(output)
        if output_size > self._input_size * (1 - MIN_SAVING):
            self._remove_output()
            return self._finish(Result(
                Status.NOT_SMALLER, self._input_size, output_size, repaired=repaired,
            ))

        self._finish(Result(
            Status.COMPRESSED, self._input_size, output_size,
            output_path=self.output, repaired=repaired,
        ))

    def _stage_and_retry(self):
        self._remove_output()
        self._staged = os.path.join(self.workdir, f'{uuid.uuid4().hex}-input.pdf')
        Gio.File.new_for_path(self.source).copy_async(
            Gio.File.new_for_path(self._staged), Gio.FileCopyFlags.NONE,
            GLib.PRIORITY_DEFAULT, self._cancellable, None, self._on_staged,
        )

    def _on_staged(self, source, res):
        try:
            source.copy_finish(res)
        except GLib.Error as e:
            if self._cancellable.is_cancelled():
                return self._finish(Result(Status.CANCELLED, self._input_size))
            return self._finish(Result(
                Status.FAILED, self._input_size, error=ErrorKind.READ_FAILED, details=e.message,
            ))
        self._spawn(self._staged)

    def _remove_output(self):
        if self.output:
            try:
                os.unlink(self.output)
            except FileNotFoundError:
                pass

    def _fail_later(self, kind, details=''):
        # Keep callbacks asynchronous even for early failures.
        size = getattr(self, '_input_size', 0)
        GLib.idle_add(lambda: self._finish(Result(Status.FAILED, size, error=kind, details=details)))

    def _finish(self, result):
        if self._staged:
            try:
                os.unlink(self._staged)
            except FileNotFoundError:
                pass
        if not self._finished:
            self._finished = True
            self._on_finished(result)
        return GLib.SOURCE_REMOVE
