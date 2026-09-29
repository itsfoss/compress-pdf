# SPDX-License-Identifier: GPL-3.0-or-later
moduledir = pkgdatadir / 'compress_pdf'

blueprints = custom_target('blueprints',
  input: files(
    'compress_pdf/ui/window.blp',
  ),
  output: '.',
  command: [find_program('blueprint-compiler'), 'batch-compile', '@OUTPUT@', '@CURRENT_SOURCE_DIR@', '@INPUT@'],
)

gnome.compile_resources('compress-pdf',
  'compress-pdf.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
  dependencies: blueprints,
)

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('VERSION', meson.project_version())
conf.set('APPLICATION_ID', application_id)
conf.set('localedir', localedir)
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'compress-pdf.in',
  output: 'compress-pdf',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'r-xr-xr-x',
)

install_subdir('compress_pdf', install_dir: pkgdatadir, exclude_directories: ['ui', '__pycache__'])
