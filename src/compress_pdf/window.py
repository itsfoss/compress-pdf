# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 It's FOSS

import os
import sys

from gi.repository import Adw, Gdk, Gio, GLib, Gtk

from .batch import Batch
from .compressor import Status, is_pdf
from .file_row import FileRow
from .levels import DEFAULT_LEVEL, LEVELS, get_level
from .naming import output_name


@Gtk.Template(resource_path='/com/itsfoss/CompressPDF/compress_pdf/ui/window.ui')
class CompressPdfWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'CompressPdfWindow'

    toast_overlay = Gtk.Template.Child()
    stack = Gtk.Template.Child()
    files_group = Gtk.Template.Child()
    add_row = Gtk.Template.Child()
    level_group = Gtk.Template.Child()
    done_group = Gtk.Template.Child()
    drop_overlay = Gtk.Template.Child()
    add_button = Gtk.Template.Child()
    bottom_bar = Gtk.Template.Child()
    compress_button = Gtk.Template.Child()
    cancel_button = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings = self.get_application().settings
        self.settings.bind('window-width', self, 'default-width', Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind('window-height', self, 'default-height', Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind('window-maximized', self, 'maximized', Gio.SettingsBindFlags.DEFAULT)

        # Files waiting to be compressed, and files already processed.
        # Only `rows` is ever handed to a batch.
        self.rows = []
        self.done_rows = []
        self.batch = None
        self._batch_rows = []
        self._close_after_cancel = False
        self._close_dialog = None

        self._add_action('add-files', self.on_add_files, '<primary>o')
        self._add_action('compress', self.on_compress, '<primary>Return')
        self._add_action('cancel', self.on_cancel)

        self._build_level_rows()
        self._setup_drop_target()
        self.connect('close-request', self.on_close_request)
        self._update_state()

    # --- setup --------------------------------------------------------------

    def _add_action(self, name, callback, accel=None):
        action = Gio.SimpleAction.new(name, None)
        action.connect('activate', lambda *args: callback())
        self.add_action(action)
        if accel:
            self.get_application().set_accels_for_action(f'win.{name}', [accel])

    def _build_level_rows(self):
        current = self.settings.get_string('level')
        if current not in {level.id for level in LEVELS}:
            current = DEFAULT_LEVEL
        group = None
        self.level_checks = {}
        for level in LEVELS:
            check = Gtk.CheckButton(valign=Gtk.Align.CENTER, active=level.id == current)
            if group:
                check.set_group(group)
            group = group or check
            check.connect('toggled', self._on_level_toggled, level.id)

            row = Adw.ActionRow(title=_(level.label), subtitle=_(level.description))
            row.add_prefix(check)
            row.set_activatable_widget(check)
            self.level_group.add(row)
            self.level_checks[level.id] = check

    def _setup_drop_target(self):
        target = Gtk.DropTarget.new(Gdk.FileList, Gdk.DragAction.COPY)
        target.connect('enter', self._on_drop_enter)
        target.connect('leave', lambda *args: self.drop_overlay.set_visible(False))
        target.connect('drop', self._on_drop)
        self.add_controller(target)

    # --- state --------------------------------------------------------------

    @property
    def running(self):
        return self.batch is not None

    def _update_state(self):
        has_files = bool(self.rows)
        has_any = has_files or bool(self.done_rows)
        self.stack.set_visible_child_name('files' if has_any else 'empty')
        self.add_button.set_visible(has_any)
        self.bottom_bar.set_visible(has_any)
        self.add_row.set_visible(not has_files and not self.running)
        self.done_group.set_visible(bool(self.done_rows))
        self.compress_button.set_visible(not self.running)
        self.cancel_button.set_visible(self.running)
        self.lookup_action('add-files').set_enabled(not self.running)
        self.lookup_action('compress').set_enabled(has_files and not self.running)
        self.lookup_action('cancel').set_enabled(self.running)
        self.level_group.set_sensitive(not self.running)
        for row in self.rows:
            row.set_busy(self.running)

        total = sum(row.size for row in self.rows)
        self.files_group.set_description(
            ngettext('{count} file, {size}', '{count} files, {size} in total', len(self.rows)).format(
                count=len(self.rows), size=GLib.format_size(total),
            ) if self.rows else None
        )
        if has_files and not self.running:
            self.set_default_widget(self.compress_button)

    def _toast(self, title, button_label=None, callback=None, timeout=5):
        toast = Adw.Toast(title=title, timeout=timeout)
        if button_label:
            toast.set_button_label(button_label)
            toast.connect('button-clicked', lambda *args: callback())
        self.toast_overlay.add_toast(toast)

    # --- adding files -------------------------------------------------------

    def add_files(self, files):
        if self.running:
            self._toast(_('Wait for the current files to finish'))
            return

        pending = {row.path for row in self.rows}
        done = {row.path: row for row in self.done_rows}
        rejected = []
        for file in files:
            path = file.get_path()
            if not path or not os.path.isfile(path):
                rejected.append(file.get_basename() or file.get_uri())
                continue
            if path in pending:
                continue
            if not is_pdf(path):
                rejected.append(file.get_basename())
                continue
            if path in done:
                # Adding a finished file again is how you ask to redo it.
                self.done_group.remove(done.pop(path))
                self.done_rows = list(done.values())
            row = FileRow(file, path, os.path.getsize(path))
            row.connect('remove', self._on_row_remove)
            self.files_group.add(row)
            self.rows.append(row)
            pending.add(path)

        if len(rejected) == 1:
            self._toast(_('“{name}” is not a PDF file').format(name=rejected[0]))
        elif rejected:
            self._toast(ngettext(
                '{count} file is not a PDF and was skipped',
                '{count} files are not PDFs and were skipped',
                len(rejected),
            ).format(count=len(rejected)))
        self._update_state()

    @Gtk.Template.Callback()
    def on_clear_done(self, *args):
        for row in self.done_rows:
            self.done_group.remove(row)
        self.done_rows = []
        self._update_state()

    def _on_row_remove(self, row):
        self.files_group.remove(row)
        self.rows.remove(row)
        self._update_state()

    def on_add_files(self):
        pdf_filter = Gtk.FileFilter(name=_('PDF Files'))
        pdf_filter.add_mime_type('application/pdf')
        pdf_filter.add_suffix('pdf')
        filters = Gio.ListStore.new(Gtk.FileFilter)
        filters.append(pdf_filter)

        dialog = Gtk.FileDialog(title=_('Select PDF Files'), filters=filters, default_filter=pdf_filter)
        dialog.open_multiple(self, None, self._on_files_chosen)

    def _on_files_chosen(self, dialog, res):
        try:
            files = dialog.open_multiple_finish(res)
        except GLib.Error:
            return  # dismissed
        self.add_files([files.get_item(i) for i in range(files.get_n_items())])

    def _on_drop_enter(self, *args):
        if self.running:
            return 0
        self.drop_overlay.set_visible(True)
        return Gdk.DragAction.COPY

    def _on_drop(self, target, value, x, y):
        self.drop_overlay.set_visible(False)
        self.add_files(value.get_files())
        return True

    def _on_level_toggled(self, check, level_id):
        if check.get_active():
            self.settings.set_string('level', level_id)

    # --- compressing --------------------------------------------------------

    def on_compress(self):
        if not self.rows or self.running:
            return
        first = self.rows[0].file
        dialog = Gtk.FileDialog(modal=True)
        parent = first.get_parent()
        if parent:
            dialog.set_initial_folder(parent)

        if len(self.rows) == 1:
            dialog.set_title(_('Save Compressed PDF'))
            dialog.set_initial_name(output_name(first.get_basename()))
            dialog.save(self, None, self._on_save_chosen)
        else:
            dialog.set_title(_('Choose Where to Save the Compressed Files'))
            dialog.set_accept_label(_('_Save Here'))
            dialog.select_folder(self, None, self._on_folder_chosen)

    def _on_save_chosen(self, dialog, res):
        try:
            target = dialog.save_finish(res)
        except GLib.Error:
            return
        self._start(target.get_path(), single=True)

    def _on_folder_chosen(self, dialog, res):
        try:
            folder = dialog.select_folder_finish(res)
        except GLib.Error:
            return
        self._start(folder.get_path(), single=False)

    def _start(self, destination, single):
        if not destination:
            self._toast(_('That location can’t be used. Choose a folder on this computer.'))
            return
        level = get_level(self.settings.get_string('level'))
        self._batch_rows = list(self.rows)
        self.batch = Batch([row.path for row in self._batch_rows], level, destination, single)
        for row in self._batch_rows:
            row.set_waiting()
        self._update_state()
        self.batch.start(
            self._on_item_started, self._on_item_progress,
            self._on_item_finished, self._on_batch_finished,
        )

    def _on_item_started(self, index):
        self._batch_rows[index].set_started()

    def _on_item_progress(self, index, done, total):
        self._batch_rows[index].set_progress(done, total)

    def _on_item_finished(self, index, result, saved_path):
        self._batch_rows[index].set_result(result, saved_path)
        if result.status is Status.FAILED and result.details:
            print(f'{self._batch_rows[index].path}: {result.error.value}\n{result.details}', file=sys.stderr)

    def _on_batch_finished(self, cancelled):
        results = self.batch.results
        self.batch = None
        if self._close_dialog:
            # Finished while we were asking whether to stop: nothing to ask any more.
            self._close_dialog.force_close()
            self._close_dialog = None
        # Processed files move to "Done"; ones that never finished stay queued.
        for row, result in zip(self._batch_rows, results):
            if result is None or result.status is Status.CANCELLED:
                row.reset()
                continue
            self.files_group.remove(row)
            self.rows.remove(row)
            self.done_group.add(row)
            self.done_rows.append(row)
        self._batch_rows = []
        self._update_state()

        if self._close_after_cancel:
            self.close()
            return
        self._show_summary(results, cancelled)

    def _show_summary(self, results, cancelled):
        done = [r for r in results if r and r.status is Status.COMPRESSED]
        if cancelled:
            self._toast(_('Compression cancelled'))
        elif done:
            saved = sum(r.input_size - r.output_size for r in done)
            title = ngettext(
                '{count} file compressed, {size} saved',
                '{count} files compressed, {size} saved',
                len(done),
            ).format(count=len(done), size=GLib.format_size(saved))
            last = Gio.File.new_for_path(done[-1].output_path)
            self._toast(title, _('Show in Folder'), lambda: self._show_in_folder(last))
        elif all(r and r.status is Status.NOT_SMALLER for r in results):
            self._toast(_('These files are already as small as this level can make them'))
        else:
            self._toast(_('No files could be compressed'))

    def _show_in_folder(self, file):
        Gtk.FileLauncher.new(file).open_containing_folder(self, None, None)

    def on_cancel(self):
        if self.batch:
            self.batch.cancel()

    # --- closing ------------------------------------------------------------

    def on_close_request(self, *args):
        if not self.running:
            return False

        dialog = Adw.AlertDialog(
            heading=_('Stop Compressing?'),
            body=_('Files that are not finished yet will not be saved.'),
        )
        dialog.add_response('keep', _('_Keep Compressing'))
        dialog.add_response('stop', _('_Stop and Close'))
        dialog.set_response_appearance('stop', Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.set_default_response('keep')
        dialog.set_close_response('keep')
        dialog.connect('response', self._on_close_response)
        dialog.connect('closed', lambda *args: setattr(self, '_close_dialog', None))
        self._close_dialog = dialog
        dialog.present(self)
        return True

    def _on_close_response(self, dialog, response):
        if response != 'stop':
            return
        if self.batch:
            self._close_after_cancel = True
            self.batch.cancel()
        else:
            self.close()
