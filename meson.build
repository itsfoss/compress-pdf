# SPDX-License-Identifier: GPL-3.0-or-later
project('compress-pdf',
  version: '3.0.0',
  meson_version: '>= 1.0.0',
  license: 'GPL-3.0-or-later',
)

i18n = import('i18n')
gnome = import('gnome')
python = import('python')

application_id = 'com.itsfoss.CompressPDF'
pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
localedir = get_option('prefix') / get_option('localedir')

subdir('data')
subdir('src')
subdir('po')

gnome.post_install(
  glib_compile_schemas: true,
  gtk_update_icon_cache: true,
  update_desktop_database: true,
)
