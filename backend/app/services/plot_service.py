"""
Draws the three graphs as PNG images (used in the PDF report).
The frontend draws its own interactive versions from the same stored data.
"""

from io import BytesIO

from matplotlib.figure import Figure

FIG_W, FIG_H = 7, 2.6   # keep the same ratio everywhere (report.py relies on it)
RED = "#e11d48"


def _to_png(fig):
    fig.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=150)
    buf.seek(0)
    return buf


def ppg_plot(t, y):
    fig = Figure(figsize=(FIG_W, FIG_H))
    ax = fig.subplots()
    ax.plot(t, y, color=RED, linewidth=1.2)
    ax.set_title("Processed PPG signal")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude (normalized)")
    ax.grid(alpha=0.3)
    return _to_png(fig)


def spectrum_plot(freqs, power, dominant_hz):
    fig = Figure(figsize=(FIG_W, FIG_H))
    ax = fig.subplots()
    ax.plot(freqs, power, color="#2563eb", linewidth=1.2)
    ax.axvline(dominant_hz, color=RED, linestyle="--")
    ax.annotate(f"{dominant_hz * 60:.0f} BPM", xy=(dominant_hz, 1.0),
                xytext=(6, -12), textcoords="offset points", color=RED)
    ax.set_title("Frequency spectrum")
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Relative power")
    ax.grid(alpha=0.3)
    return _to_png(fig)


def history_plot(bpms_oldest_first):
    fig = Figure(figsize=(FIG_W, FIG_H))
    ax = fig.subplots()
    ax.plot(range(1, len(bpms_oldest_first) + 1), bpms_oldest_first,
            marker="o", color=RED)
    ax.set_title("Heart rate history (oldest to newest)")
    ax.set_xlabel("Measurement number")
    ax.set_ylabel("Estimated BPM")
    ax.grid(alpha=0.3)
    return _to_png(fig)