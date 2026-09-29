#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Compare compression levels on a folder of PDFs.

    tools/bench.py ~/some/pdfs [--keep OUTDIR]

Uses the same Ghostscript arguments as the app. Keep the sample PDFs
outside the repository.
"""

import argparse
import builtins
import os
import shutil
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
builtins.__dict__.setdefault('_', lambda s: s)

from compress_pdf.compressor import build_args, find_ghostscript  # noqa: E402
from compress_pdf.levels import LEVELS  # noqa: E402


def human(n):
    for unit in ('B', 'KB', 'MB', 'GB'):
        if n < 1024 or unit == 'GB':
            return f'{n:.0f} {unit}' if unit == 'B' else f'{n:.1f} {unit}'
        n /= 1024


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('folder')
    parser.add_argument('--keep', metavar='OUTDIR', help='keep the compressed files here')
    parser.add_argument('--anonymous', action='store_true', help='print file numbers instead of names')
    args = parser.parse_args()

    gs = find_ghostscript()
    if not gs:
        sys.exit('Ghostscript (gs) not found')

    files = sorted(f for f in os.listdir(args.folder) if f.lower().endswith('.pdf'))
    workdir = args.keep or tempfile.mkdtemp(prefix='compress-pdf-bench-')
    os.makedirs(workdir, exist_ok=True)

    header = f'{"file":<28} {"original":>10} ' + ' '.join(f'{lv.id:>18}' for lv in LEVELS)
    print(header)
    print('-' * len(header))
    for i, name in enumerate(files, 1):
        src = os.path.join(args.folder, name)
        size = os.path.getsize(src)
        label = f'#{i}' if args.anonymous else name[:28]
        cells = []
        for level in LEVELS:
            out = os.path.join(workdir, f'{os.path.splitext(name)[0]}.{level.id}.pdf')
            t0 = time.monotonic()
            proc = subprocess.run(build_args(gs, src, out, level), capture_output=True, env={**os.environ, 'LC_ALL': 'C'})
            took = time.monotonic() - t0
            if proc.returncode or not os.path.exists(out):
                cells.append(f'{"failed":>18}')
                continue
            new = os.path.getsize(out)
            cells.append(f'{human(new):>9} {(new - size) * 100 / size:+4.0f}% {took:3.0f}s')
        print(f'{label:<28} {human(size):>10} ' + ' '.join(cells), flush=True)

    if not args.keep:
        shutil.rmtree(workdir)


if __name__ == '__main__':
    main()
