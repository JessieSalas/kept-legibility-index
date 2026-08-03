import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ['VISIONOCR'] = '/private/tmp/claude-501/-Users-jessiesalas-Projects-numen/f4beaa10-7ad8-4a12-8f80-6d313aefa192/scratchpad/kept-type/kept-type/ocr/visionocr'
import bench_v31
K = '/private/tmp/claude-501/-Users-jessiesalas-Projects-numen/f4beaa10-7ad8-4a12-8f80-6d313aefa192/scratchpad/kept-type/kept-type'
B = f'{K}/basefonts'
REPO = '/Users/jessiesalas/Projects/numen'
SUP = '/System/Library/Fonts/Supplemental'
FONTS = [
    ('Legibility Sans',   f'{K}/legibilitysans/dist/LegibilitySans-Regular.ttf', 0, None),
    ('Kept Sans',         f'{K}/keptsans/dist-v2/KeptSans-Regular.ttf', 0, None),
    ('Numen Title',       f'{K}/numentitle/dist/NumenTitle-Regular.ttf', 0, None),
    ('Verdana',           f'{SUP}/Verdana.ttf', 0, None),
    ('Georgia',           f'{SUP}/Georgia.ttf', 0, None),
    ('Arial',             f'{SUP}/Arial.ttf', 0, None),
    ('Times New Roman',   f'{SUP}/Times New Roman.ttf', 0, None),
    ('Charter',           f'{SUP}/Charter.ttc', 0, None),
    ('SF Pro',            '/System/Library/Fonts/SFNS.ttf', 0, None),
    ('Helvetica Neue',    '/System/Library/Fonts/HelveticaNeue.ttc', 0, None),
    ('Comic Sans MS',     f'{SUP}/Comic Sans MS.ttf', 0, None),
    ('Inter',             f'{REPO}/packages/KeptKit/Sources/KeptKit/Resources/Fonts/Inter-Regular.ttf', 0, None),
    ('Roboto',            f'{B}/roboto.ttf', 0, 400),
    ('Figtree',           f'{B}/figtree.ttf', 0, 400),
    ('Atkinson Hyperlegible', f'{B}/atkinson.ttf', 0, None),
    ('Atkinson Next',     f'{B}/atkinsonnext.ttf', 0, 400),
    ('Lexend',            f'{B}/lexend.ttf', 0, 400),
    ('OpenDyslexic',      f'{B}/opendyslexic.otf', 0, None),
    ('Andika',            f'{B}/andika.ttf', 0, None),
    ('Noto Sans',         f'{B}/notosans.ttf', 0, 400),
    ('Source Sans 3',     f'{B}/sourcesans3.ttf', 0, 400),
    ('IBM Plex Sans',     f'{B}/ibmplexsans.ttf', 0, 400),
    ('Public Sans',       f'{B}/publicsans.ttf', 0, 400),
    ('Instrument Serif',  f'{B}/instrumentserif.ttf', 0, None),
]
bench_v31.run(FONTS, out_name='results-v31-OFFICIAL.json', keep_raw=True)
