"""Usage:  python try_video.py "C:\\path\\to\\video.mp4" [green|red]"""

import sys

from app.processing.heart_rate import analyze_video
from app.utils.errors import PulseLensError

if len(sys.argv) < 2:
    print('Usage: python try_video.py "path\\to\\video.mp4" [green|red]')
    sys.exit(1)

channel = sys.argv[2] if len(sys.argv) > 2 else "green"
try:
    r = analyze_video(sys.argv[1], channel=channel)
except PulseLensError as e:
    print("Could not analyze:", e.message)
    sys.exit(1)

print(f"Channel:        {channel}")
print(f"Video length:   {r['duration_seconds']} s at {r['fps']} FPS")
print(f"Estimated BPM:  {r['bpm']}")
print(f"Signal quality: {r['quality_label']} (score {r['quality_score']})")
print(f"Dominant freq:  {r['dominant_frequency_hz']} Hz")
print("Message:       ", r["message"] or r["interpretation"])