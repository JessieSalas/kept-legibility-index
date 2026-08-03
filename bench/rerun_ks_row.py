import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ['VISIONOCR'] = '/private/tmp/claude-501/-Users-jessiesalas-Projects-numen/f4beaa10-7ad8-4a12-8f80-6d313aefa192/scratchpad/kept-type/kept-type/ocr/visionocr'
import bench_v31
K = '/private/tmp/claude-501/-Users-jessiesalas-Projects-numen/f4beaa10-7ad8-4a12-8f80-6d313aefa192/scratchpad/kept-type/kept-type'
bench_v31.run([
    ('Kept Sans', f'{K}/keptsans/dist-v2/KeptSans-Regular.ttf', 0, None),
], out_name='ks-fixed-row.json', keep_raw=True)
