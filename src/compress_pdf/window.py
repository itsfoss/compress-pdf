# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 It's FOSS

from gi.repository import Adw, Gio, Gtk


@Gtk.Template(resource_path='/com/itsfoss/CompressPDF/compress_pdf/ui/window.ui')
class CompressPdfWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'CompressPdfWindow'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        settings = self.get_application().settings
        settings.bind('window-width', self, 'default-width', Gio.SettingsBindFlags.DEFAULT)
        settings.bind('window-height', self, 'default-height', Gio.SettingsBindFlags.DEFAULT)
        settings.bind('window-maximized', self, 'maximized', Gio.SettingsBindFlags.DEFAULT)

    def add_files(self, files):
        # Wired up in milestone 3.
        pass
