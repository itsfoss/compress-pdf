# SPDX-License-Identifier: GPL-3.0-or-later
moduledir = pkgdatadir / 'compress_pdf'

# One target per file with an explicit output, so edits trigger a rebuild.
blueprint_compiler = find_program('blueprint-compiler')
blueprints = []
foreach blp : ['window']
  blueprints += custom_target(blp + '.ui',
    input: 'compress_pdf/ui' / blp + '.blp',
    output: blp + '.ui',
    command: [blueprint_compiler, 'compile', '--output', '@OUTPUT@', '@INPUT@'],
  )
endforeach

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

install_subdir('compress_pdf', install_dir: pkgdatadir, exclude_directories: ['ui', '__pycache__'],
  exclude_files: ['style.css'])
