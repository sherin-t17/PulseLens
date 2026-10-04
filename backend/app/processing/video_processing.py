"""
Video -> 1D signal.

PPG idea: when the heart beats, the amount of blood in the fingertip changes
slightly. With a finger over the camera (flash on), more blood means more light
absorbed, so the average brightness of the video changes tiny bit by tiny bit
in rhythm with the pulse. We measure that average brightness for every frame.
"""

import cv2
import numpy as np

from app.utils.errors import PulseLensError

# OpenCV stores colors as Blue, Green, Red (BGR), NOT RGB.
CHANNEL_INDEX = {"blue": 0, "green": 1, "red": 2}


def extract_green_signal(video_path, roi_fraction=0.5, channel="green"):
    """
    Read a video and return one brightness value per frame.

    roi_fraction: use only the central part of the frame (0.5 = the middle
                  50% of width and height). Edges often contain shadows,
                  finger edges or background, which add noise.
    channel:      "green" (default, as in the project spec) or "red"
                  (often stronger with flash + fingertip; good to compare).

    Returns: (signal, fps, mean_bgr)
      signal   - numpy array, one value per frame (resampled to a uniform rate)
      fps      - effective frames per second of that signal
      mean_bgr - average (B, G, R) over the whole video, used to check that a
                 finger was actually covering the camera
    """
    if channel not in CHANNEL_INDEX:
        raise PulseLensError("Unknown color channel.")

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise PulseLensError(
            "The video could not be opened. Please upload a valid MP4 or AVI file."
        )

    reported_fps = cap.get(cv2.CAP_PROP_FPS)
    values, times, bgr_means = [], [], []

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            # --- Region of interest (ROI): a centered rectangle -------------
            h, w = frame.shape[:2]
            dh = int(h * (1 - roi_fraction) / 2)
            dw = int(w * (1 - roi_fraction) / 2)
            roi = frame[dh:h - dh, dw:w - dw]

            # Mean of each color channel inside the ROI -> [B, G, R]
            mean_bgr = roi.reshape(-1, 3).mean(axis=0)
            bgr_means.append(mean_bgr)
            values.append(mean_bgr[CHANNEL_INDEX[channel]])

            # Timestamp of this frame in seconds (handles uneven frame timing)
            times.append(cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0)
    finally:
        cap.release()

    if len(values) < 30:
        raise PulseLensError("The video has too few frames. Please record a longer video.")

    values = np.asarray(values, dtype=float)
    times = np.asarray(times, dtype=float)
    mean_bgr_overall = np.mean(bgr_means, axis=0)

    # --- Decide the sampling rate ----------------------------------------
    # Prefer real timestamps. If they are unusable (all zeros / not increasing),
    # fall back to the FPS reported by the file.
    timestamps_ok = times[-1] > times[0] and np.all(np.diff(times) >= 0)
    if timestamps_ok:
        duration = times[-1] - times[0]
        fps = (len(values) - 1) / duration
        # Resample onto an evenly spaced time grid (FFT assumes even spacing).
        even_times = np.linspace(times[0], times[-1], len(values))
        values = np.interp(even_times, times, values)
    elif reported_fps and reported_fps > 1:
        fps = float(reported_fps)
    else:
        raise PulseLensError("Could not determine the video frame rate (FPS).")

    return values, float(fps), mean_bgr_overall