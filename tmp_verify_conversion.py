import json
import tempfile
import os
from data.pipeline.conversion.conversion_tracker import ConversionTracker

sample_tracks = [{'frame': 1, 'track_id': i, 'center_x': 960, 'center_y': 150} for i in range(1, 11)]
sample_pos = [{'transaction_id': 'TXN_001', 'timestamp': '2026-05-30T10:05:00Z', 'amount': 100.00}]

with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tfile:
    json.dump(sample_tracks, tfile)
    tracks_path = tfile.name

with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as pfile:
    json.dump(sample_pos, pfile)
    pos_path = pfile.name

try:
    tracker = ConversionTracker()
    tracker.load_tracks(tracks_path)
    tracker.load_pos_data(pos_path)
    tracker.correlate_conversions()
    stats = tracker.get_conversion_stats()
    print('stats', stats)
    print('converted', [s.visitor_id for s in tracker.sessions.values() if s.converted])
finally:
    os.unlink(tracks_path)
    os.unlink(pos_path)
