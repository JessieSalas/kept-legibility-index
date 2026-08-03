import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ['VISIONOCR'] = '/private/tmp/claude-501/-Users-jessiesalas-Projects-numen/f4beaa10-7ad8-4a12-8f80-6d313aefa192/scratchpad/kept-type/kept-type/ocr/visionocr'
import bench_v31
K = '/private/tmp/claude-501/-Users-jessiesalas-Projects-numen/f4beaa10-7ad8-4a12-8f80-6d313aefa192/scratchpad/kept-type/kept-type'
V = f'{K}/variants'
bench_v31.run([
    ('Verdana',         '/System/Library/Fonts/Supplemental/Verdana.ttf', 0, None),
    ('LS11 a current',  f'{V}/LS11-a-current.ttf', 0, None),
    ('LS11 g zero',     f'{V}/LS11-g-zero.ttf', 0, None),
    ('LS11 h sp14t8',   f'{V}/LS11-h-sp14t8.ttf', 0, None),
    ('LS11 i zero sp14', f'{V}/LS11-i-zero-sp14.ttf', 0, None),
], out_name='select2-v31.json', keep_raw=False)
