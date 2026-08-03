import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ['VISIONOCR'] = '/private/tmp/claude-501/-Users-jessiesalas-Projects-numen/f4beaa10-7ad8-4a12-8f80-6d313aefa192/scratchpad/kept-type/kept-type/ocr/visionocr'
import bench_v31
K = '/private/tmp/claude-501/-Users-jessiesalas-Projects-numen/f4beaa10-7ad8-4a12-8f80-6d313aefa192/scratchpad/kept-type/kept-type'
V = f'{K}/variants'
bench_v31.run([
    ('Verdana',        '/System/Library/Fonts/Supplemental/Verdana.ttf', 0, None),
    ('LS11 a current', f'{V}/LS11-a-current.ttf', 0, None),
    ('LS11 b wide105', f'{V}/LS11-b-wide105.ttf', 0, None),
    ('LS11 c wide dh', f'{V}/LS11-c-wide-dhold.ttf', 0, None),
    ('LS11 d c w445',  f'{V}/LS11-d-c-w445.ttf', 0, None),
    ('LS11 e dhold',   f'{V}/LS11-e-dhold.ttf', 0, None),
    ('LS11 f wide108', f'{V}/LS11-f-wide108.ttf', 0, None),
], out_name='select-v31.json', keep_raw=False)
