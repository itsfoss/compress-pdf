# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 It's FOSS

from gi.repository import Adw, Gio, GLib, GObject, Gtk

from . import errors
from .compressor import Status


class FileRow(Adw.ActionRow):
    """One file in the list: name, size, then progress and the result."""

    __gtype_name__ = 'CompressPdfFileRow'
    __gsignals__ = {'remove': (GObject.SignalFlags.RUN_FIRST, None, ())}

    def __init__(self, file, path, size):
        super().__init__(use_markup=False, title=file.get_basename(), subtitle_lines=2)
        self.file = file
        self.path = path
        self.size = size
        self.saved_path = None

        self.add_prefix(Gtk.Image(icon_name='x-office-document-symbolic'))

        self._remove_button = Gtk.Button(
            icon_name='window-close-symbolic', valign=Gtk.Align.CENTER,
            tooltip_text=_('Remove'), css_classes=['flat', 'circular'],
        )
        self._remove_button.update_property([Gtk.AccessibleProperty.LABEL], [_('Remove')])
        self._remove_button.connect('clicked', lambda *args: self.emit('remove'))

        self._progress = Gtk.ProgressBar(valign=Gtk.Align.CENTER, width_request=80)

        self._status_icon = Gtk.Image(valign=Gtk.Align.CENTER)

        self._open_button = Gtk.Button(
            label=_('Open'), valign=Gtk.Align.CENTER, css_classes=['flat'],
        )
        self._open_button.connect('clicked', self._on_open)

        self._suffix = Gtk.Stack(hhomogeneous=False, interpolate_size=True)
        self._suffix.add_named(self._remove_button, 'remove')
        self._suffix.add_named(self._progress, 'progress')
        self._suffix.add_named(self._status_icon, 'status')
        self._suffix.add_named(self._open_button, 'open')
        self.add_suffix(self._suffix)

        self.reset()

    def reset(self):
        self.saved_path = None
        self.set_subtitle(GLib.format_size(self.size))
        self._suffix.set_visible_child_name('remove')

    def set_busy(self, busy):
        """While a batch runs, rows can't be removed."""
        self._remove_button.set_sensitive(not busy)

    def set_waiting(self):
        self.reset()
        self.set_subtitle(_('Waiting…'))
        self._show_status('content-loading-symbolic', _('Waiting'))

    def set_started(self):
        self._progress.set_fraction(0)
        self.set_subtitle(_('Starting…'))
        self._suffix.set_visible_child_name('progress')

    def set_progress(self, done, total):
        self._progress.set_fraction(done / total if total else 0)
        # Translators: progress while compressing, e.g. “Page 12 of 47”
        self.set_subtitle(_('Page {done} of {total}').format(done=done, total=total))

    def set_result(self, result, saved_path):
        self.saved_path = saved_path
        if result.status is Status.COMPRESSED:
            text = _('{old} → {new} ({percent}% smaller)').format(
                old=GLib.format_size(result.input_size),
                new=GLib.format_size(result.output_size),
                # Round down and cap, so a tiny file never reads as “100% smaller”.
                percent=min(int(result.saving * 100), 99),
            )
            if result.repaired:
                text += ' · ' + _('Damaged file repaired')
            self.set_subtitle(text)
            self._suffix.set_visible_child_name('open')
        elif result.status is Status.NOT_SMALLER:
            self.set_subtitle(_('Already optimised, not saved'))
            self._show_status('object-select-symbolic', _('Already optimised'), 'success')
        elif result.status is Status.CANCELLED:
            self.set_subtitle(_('Cancelled'))
            self._show_status('process-stop-symbolic', _('Cancelled'))
        else:
            self.set_subtitle(errors.message(result.error))
            self._show_status('dialog-warning-symbolic', _('Failed'), 'error')

    def set_cancelled(self):
        self.set_subtitle(_('Cancelled'))
        self._show_status('process-stop-symbolic', _('Cancelled'))

    def _show_status(self, icon_name, tooltip, style=None):
        self._status_icon.set_css_classes([style] if style else [])
        self._status_icon.set_from_icon_name(icon_name)
        self._status_icon.set_tooltip_text(tooltip)
        self._status_icon.update_property([Gtk.AccessibleProperty.LABEL], [tooltip])
        self._suffix.set_visible_child_name('status')

    def _on_open(self, *args):
        if not self.saved_path:
            return
        launcher = Gtk.FileLauncher.new(Gio.File.new_for_path(self.saved_path))
        launcher.launch(self.get_root(), None, None)

