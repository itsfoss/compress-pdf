# SPDX-License-Identifier: GPL-3.0-or-later
pytest = find_program('pytest-3', 'pytest', required: false)
if pytest.found()
  test('Unit tests', pytest,
    args: ['-q', meson.current_source_dir()],
    timeout: 600,
  )
endif
