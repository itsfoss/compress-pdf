# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 It's FOSS
"""Compress a list of files one after another and save the results.

No GTK in here, so it can be tested without a display.
"""

import os

from gi.repository import Gio, GLib

from .compressor import CompressionJob, Status
from .errors import ErrorKind
from .naming import output_name, unique_path


class Batch:
    """Compress `sources` and save them.

    `destination` is a path: the output file when `single` is true,
    otherwise a folder that gets <name>-compressed.pdf for every file.

    Callbacks, all on the main loop:
      on_item_started(index)
      on_item_progress(index, done, total)
      on_item_finished(index, result, saved_path_or_None)
      on_finished(cancelled)
    """

    def __init__(self, sources, level, destination, single, gs=None, workdir=None):
        self.sources = list(sources)
        self.level = level
        self.destination = destination
        self.single = single
        self.gs = gs
        self.workdir = workdir
        self.results = [None] * len(self.sources)
        self._index = -1
        self._job = None
        self._cancellable = Gio.Cancellable()
        self._taken = set()

    @property
    def running(self):
        return 0 <= self._index < len(self.sources)

    def start(self, on_item_started, on_item_progress, on_item_finished, on_finished):
        self._on_item_started = on_item_started
        self._on_item_progress = on_item_progress
        self._on_item_finished = on_item_finished
        self._on_finished = on_finished
        self._next()

    def cancel(self):
        self._cancellable.cancel()
        if self._job:
            self._job.cancel()

    def _next(self):
        self._index += 1
        if self._cancellable.is_cancelled() or self._index >= len(self.sources):
            self._job = None
            self._on_finished(self._cancellable.is_cancelled())
            return

        index = self._index
        self._on_item_started(index)
        self._job = CompressionJob(self.sources[index], self.level, gs=self.gs, workdir=self.workdir)
        self._job.start(
            lambda done, total: self._on_item_progress(index, done, total),
            lambda result: self._on_compressed(index, result),
        )

    def _on_compressed(self, index, result):
        if result.status is not Status.COMPRESSED:
            self._item_done(index, result, None)
            return

        if self.single:
            target = self.destination
            # The save dialog already asked the user about overwriting.
            flags = Gio.FileCopyFlags.OVERWRITE
        else:
            target = unique_path(
                self.destination, output_name(self.sources[index]), taken=self._taken,
            )
            self._taken.add(target)
            flags = Gio.FileCopyFlags.NONE

        temp = Gio.File.new_for_path(result.output_path)
        temp.copy_async(
            Gio.File.new_for_path(target), flags, GLib.PRIORITY_DEFAULT,
            self._cancellable, None,
            lambda file, res: self._on_copied(file, res, index, result, target),
        )

    def _on_copied(self, temp, res, index, result, target):
        try:
            temp.copy_finish(res)
            saved = target
        except GLib.Error as e:
            saved = None
            if e.matches(Gio.io_error_quark(), Gio.IOErrorEnum.CANCELLED):
                result.status = Status.CANCELLED
            else:
                result.status = Status.FAILED
                result.error = ErrorKind.WRITE_FAILED
                result.details = e.message
        finally:
            try:
                os.unlink(result.output_path)
            except OSError:
                pass
        result.output_path = saved
        self._item_done(index, result, saved)

    def _item_done(self, index, result, saved):
        self.results[index] = result
        self._on_item_finished(index, result, saved)
        self._next()
