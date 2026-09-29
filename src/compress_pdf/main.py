# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 It's FOSS

import sys

from gi.repository import Adw, Gio, GLib

from .compressor import clean_workdir
from .window import CompressPdfWindow

MIN_ADW = (1, 5)


class CompressPdfApplication(Adw.Application):
    def __init__(self, version, application_id):
        super().__init__(
            application_id=application_id,
            flags=Gio.ApplicationFlags.HANDLES_OPEN,
            resource_base_path='/com/itsfoss/CompressPDF',
        )
        self.version = version
        self.settings = Gio.Settings.new(application_id)

        self.create_action('about', self.on_about)
        self.create_action('quit', lambda *args: self.quit(), ['<primary>q'])
        self.set_accels_for_action('window.close', ['<primary>w'])

    def do_startup(self):
        Adw.Application.do_startup(self)
        clean_workdir()

    def do_activate(self):
        self.get_window().present()

    def do_open(self, files, n_files, hint):
        window = self.get_window()
        window.add_files(files)
        window.present()

    def get_window(self):
        window = self.get_active_window()
        if window is None:
            window = CompressPdfWindow(application=self)
        return window

    def on_about(self, *args):
        about = Adw.AboutDialog(
            application_name=_('Compress PDF'),
            application_icon=self.get_application_id(),
            developer_name="It's FOSS",
            version=self.version,
            website='https://itsfoss.com/',
            issue_url='https://github.com/itsfoss/compress-pdf/issues',
            license_type='gpl-3-0',
            copyright="© 2019–2026 It's FOSS",
            developers=["It's FOSS https://itsfoss.com/"],
            # Translators: replace with your name and email, one per line
            translator_credits=_('translator-credits'),
        )
        about.add_link(_('Source Code'), 'https://github.com/itsfoss/compress-pdf')
        about.present(self.get_active_window())

    def create_action(self, name, callback, shortcuts=None):
        action = Gio.SimpleAction.new(name, None)
        action.connect('activate', callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f'app.{name}', shortcuts)


def main(version, application_id):
    if (Adw.get_major_version(), Adw.get_minor_version()) < MIN_ADW:
        print(
            f'Compress PDF needs libadwaita {MIN_ADW[0]}.{MIN_ADW[1]} or newer, '
            f'found {Adw.get_major_version()}.{Adw.get_minor_version()}.',
            file=sys.stderr,
        )
        return 1
    GLib.set_application_name(_('Compress PDF'))
    app = CompressPdfApplication(version, application_id)
    return app.run(sys.argv)
