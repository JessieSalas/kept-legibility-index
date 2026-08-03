"""The public entry point: runs Protocol v3 over the standard panel.

Font resolution order per face: repo fonts/ directory (fetch.sh), standard
macOS system paths, locally installed apps (Bear). Faces that cannot be found
are skipped with a notice, and the run proceeds; your table simply has fewer
rows. Kept's own faces: download kept-type.zip from kept.do/type and unzip
into fonts/kept-type/.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bench_v3

F = os.path.join(os.path.dirname(HERE), 'fonts')
SYS = '/System/Library/Fonts'
SUP = f'{SYS}/Supplemental'
KT = os.path.join(F, 'kept-type')

PANEL = [
    ('Index Sans',        f'{KT}/IndexSans/IndexSans-Regular.ttf', 0, None),
    ('Kept Sans',         f'{KT}/KeptSans/KeptSans-Regular.ttf', 0, None),
    ('Numen Title',       f'{KT}/NumenTitle/NumenTitle-Regular.ttf', 0, None),
    ('Verdana',           f'{SUP}/Verdana.ttf', 0, None),
    ('Georgia',           f'{SUP}/Georgia.ttf', 0, None),
    ('Arial',             f'{SUP}/Arial.ttf', 0, None),
    ('Times New Roman',   f'{SUP}/Times New Roman.ttf', 0, None),
    ('Charter',           f'{SUP}/Charter.ttc', 0, None),
    ('SF Pro',            f'{SYS}/SFNS.ttf', 0, None),
    ('Helvetica Neue',    f'{SYS}/HelveticaNeue.ttc', 0, None),
    ('Inter',             f'{F}/inter.ttf', 0, 400),
    ('Roboto',            f'{F}/roboto.ttf', 0, 400),
    ('Figtree',           f'{F}/figtree.ttf', 0, 400),
    ('Atkinson Hyperlegible', f'{F}/atkinson.ttf', 0, None),
    ('Atkinson Next',     f'{F}/atkinsonnext.ttf', 0, 400),
    ('Lexend',            f'{F}/lexend.ttf', 0, 400),
    ('Instrument Serif',  f'{F}/instrumentserif.ttf', 0, None),
    ('Bear Sans UI',      '/Applications/Bear.app/Contents/Resources/BearSansUI-Regular.otf', 0, None),
    ('Bear Sans Heading', '/Applications/Bear.app/Contents/Resources/BearSansUIHeading-Regular.otf', 0, None),
    ('OpenDyslexic',      '/Applications/Bear.app/Contents/Resources/OpenDyslexic-Regular.otf', 0, None),
]

fonts = []
for label, path, idx, wght in PANEL:
    if os.path.exists(path):
        fonts.append((label, path, idx, wght))
    else:
        print(f'skip (not found): {label}  [{path}]', file=sys.stderr)

bench_v3.run(fonts, out_name='results-v3.json')
