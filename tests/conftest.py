# SPDX-License-Identifier: GPL-3.0-or-later
import builtins
import os
import shutil
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
builtins.__dict__.setdefault('_', lambda s: s)
builtins.__dict__.setdefault('ngettext', lambda s, p, n: s if n == 1 else p)

GS = shutil.which('gs')
needs_gs = pytest.mark.skipif(GS is None, reason='Ghostscript not installed')

# 600 dpi colour "scan": gradients plus sensor-like noise, three pages.
IMAGE_PS = r'''%!PS
/w 1200 def /h 1200 def
/row w 3 mul string def
/s 1 def
/noise { /s s 75 mul 74 add 65537 mod def s 31 and } def
3 {
  gsave
  /y 0 def
  90 300 translate 144 144 scale
  w h 8 [w 0 0 h neg 0 h]
  { 0 1 w 1 sub { /x exch def
      row x 3 mul x 200 mul w idiv noise add put
      row x 3 mul 1 add y 200 mul h idiv noise add put
      row x 3 mul 2 add x y xor 200 and noise add put
    } for
    /y y 1 add def row }
  false 3 colorimage
  grestore
  showpage
} repeat
'''

TEXT_PS = r'''%!PS
/Helvetica findfont 12 scalefont setfont
72 720 moveto (A page with nothing but a line of text.) show
showpage
'''


def _gs(ps_source, output, *extra):
    ps = output + '.ps'
    with open(ps, 'w') as f:
        f.write(ps_source)
    subprocess.run(
        [GS, '-q', '-dSAFER', '-dBATCH', '-dNOPAUSE', '-sDEVICE=pdfwrite',
         '-dAutoFilterColorImages=false', '-dColorImageFilter=/FlateEncode',
         '-dDownsampleColorImages=false', *extra, f'-sOutputFile={output}', ps],
        check=True,
    )
    return output


@pytest.fixture(scope='session')
def samples(tmp_path_factory):
    if GS is None:
        pytest.skip('Ghostscript not installed')
    d = tmp_path_factory.mktemp('samples')
    fake = d / 'fake.pdf'
    fake.write_text('this is not a pdf\n')
    image = _gs(IMAGE_PS, str(d / 'image.pdf'))
    # %d would be expanded by Ghostscript, a leading dash looks like an option.
    odd = d / '-Résumé 100% %d (final).pdf'
    shutil.copy(image, odd)
    # 30 pages; each copy is shifted so duplicate-image detection can't skip work.
    long = str(d / 'long.pdf')
    subprocess.run(
        [GS, '-q', '-dSAFER', '-dBATCH', '-dNOPAUSE', '-sDEVICE=pdfwrite',
         '-dAutoFilterColorImages=false', '-dColorImageFilter=/FlateEncode',
         '-dDownsampleColorImages=false', '-dDetectDuplicateImages=false',
         f'-sOutputFile={long}', *[image] * 10],
        check=True,
    )
    return {
        'image': image,
        'long': long,
        'text': _gs(TEXT_PS, str(d / 'text.pdf')),
        'locked': _gs(TEXT_PS, str(d / 'locked.pdf'),
                      '-sOwnerPassword=owner', '-sUserPassword=secret', '-dEncryptionR=3', '-dKeyLength=128'),
        'fake': str(fake),
        'odd': str(odd),
    }
