# SPDX-License-Identifier: GPL-3.0-or-later
desktop_file = i18n.merge_file(
  input: configure_file(
    input: 'com.itsfoss.CompressPDF.desktop.in.in',
    output: 'com.itsfoss.CompressPDF.desktop.in',
    configuration: {'APPLICATION_ID': application_id},
  ),
  output: 'com.itsfoss.CompressPDF.desktop',
  type: 'desktop',
  po_dir: '../po',
  install: true,
  install_dir: get_option('datadir') / 'applications',
)

desktop_utils = find_program('desktop-file-validate', required: false)
if desktop_utils.found()
  test('Validate desktop file', desktop_utils, args: [desktop_file])
endif

metainfo_file = i18n.merge_file(
  input: 'com.itsfoss.CompressPDF.metainfo.xml.in',
  output: 'com.itsfoss.CompressPDF.metainfo.xml',
  po_dir: '../po',
  install: true,
  install_dir: get_option('datadir') / 'metainfo',
)

appstreamcli = find_program('appstreamcli', required: false)
if appstreamcli.found()
  test('Validate metainfo file', appstreamcli,
    args: ['validate', '--no-net', '--explain', metainfo_file])
endif

install_data('com.itsfoss.CompressPDF.gschema.xml',
  install_dir: get_option('datadir') / 'glib-2.0' / 'schemas',
)

compile_schemas = find_program('glib-compile-schemas', required: false)
if compile_schemas.found()
  test('Validate schema file', compile_schemas,
    args: ['--strict', '--dry-run', meson.current_source_dir()])
endif

install_data('icons/com.itsfoss.CompressPDF.svg',
  install_dir: get_option('datadir') / 'icons' / 'hicolor' / 'scalable' / 'apps',
)
install_data('icons/com.itsfoss.CompressPDF-symbolic.svg',
  install_dir: get_option('datadir') / 'icons' / 'hicolor' / 'symbolic' / 'apps',
)
