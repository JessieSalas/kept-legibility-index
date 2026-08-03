"""Public v3.1 driver: portable paths, same panel as the published table.
Kept faces come from fonts/kept-type/ (unzip kept-type.zip into fonts/).
Missing faces are skipped with a notice."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bench_v31

F = os.path.join(os.path.dirname(HERE), 'fonts')
KT = os.path.join(F, 'kept-type')
SUP = '/System/Library/Fonts/Supplemental'
SYS = '/System/Library/Fonts'
PANEL = [
    ('Legibility Sans', f'{KT}/LegibilitySans/LegibilitySans-Regular.ttf', 0, None),
    ('Kept Sans', f'{KT}/KeptSans/KeptSans-Regular.ttf', 0, None),
    ('Numen Title', f'{KT}/NumenTitle/NumenTitle-Regular.ttf', 0, None),
    ('Verdana', f'{SUP}/Verdana.ttf', 0, None),
    ('Georgia', f'{SUP}/Georgia.ttf', 0, None),
    ('Arial', f'{SUP}/Arial.ttf', 0, None),
    ('Times New Roman', f'{SUP}/Times New Roman.ttf', 0, None),
    ('Charter', f'{SUP}/Charter.ttc', 0, None),
    ('SF Pro', f'{SYS}/SFNS.ttf', 0, None),
    ('Helvetica Neue', f'{SYS}/HelveticaNeue.ttc', 0, None),
    ('Comic Sans MS', f'{SUP}/Comic Sans MS.ttf', 0, None),
    ('Inter', f'{F}/inter.ttf', 0, 400),
    ('Roboto', f'{F}/roboto.ttf', 0, 400),
    ('Figtree', f'{F}/figtree.ttf', 0, 400),
    ('Atkinson Hyperlegible', f'{F}/atkinson.ttf', 0, None),
    ('Atkinson Next', f'{F}/atkinsonnext.ttf', 0, 400),
    ('Lexend', f'{F}/lexend.ttf', 0, 400),
    ('OpenDyslexic', '/Applications/Bear.app/Contents/Resources/OpenDyslexic-Regular.otf', 0, None),
    ('Andika', f'{F}/andika.ttf', 0, None),
    ('Noto Sans', f'{F}/notosans.ttf', 0, 400),
    ('Source Sans 3', f'{F}/sourcesans3.ttf', 0, 400),
    ('IBM Plex Sans', f'{F}/ibmplexsans.ttf', 0, 400),
    ('Public Sans', f'{F}/publicsans.ttf', 0, 400),
    ('Instrument Serif', f'{F}/instrumentserif.ttf', 0, None),
]
fonts = []
for row in PANEL:
    if os.path.exists(row[1]):
        fonts.append(row)
    else:
        print(f'skip (not found): {row[0]}', file=sys.stderr)
bench_v31.run(fonts, out_name='results-v31.json')
