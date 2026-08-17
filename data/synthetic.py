"""Shared synthetic test data for all similarity notebooks.

Every notebook imports :func:`generate_dataset` so that DTW, EDR, ERP and the
statistical-feature approach are all compared on *exactly* the same signals.
All randomness goes through a seeded generator, so the data is identical across
runs and across notebooks.

The signals imitate a simple machine/sensor trace: a slow linear drift, two
periodic components, and a little measurement noise.  Each variant applies one
well-defined distortion to the reference, so that every notebook's distance
table isolates one property of the algorithm at a time.
"""

from __future__ import annotations

import numpy as np

# --- Generation parameters (kept at module level so notebooks can show them) ---
SEED = 42
N_SAMPLES = 300  # length of the reference series
SHIFT = 40  # time offset (in samples) used for `phase_shifted`
FS = 50.0  # nominal sampling rate in Hz, only used to build a time axis

# Distortion strengths
AMPLITUDE_FACTOR = 2.0
RESAMPLE_FACTOR = 1.3  # `resampled` is 30 % longer than the reference
BASE_NOISE_STD = 0.15  # measurement noise already present in the reference
EXTRA_NOISE_STD = 0.60  # additional noise for the `noisy` variant


def _base_signal(t: np.ndarray) -> np.ndarray:
    """Noise-free "sensor" waveform: linear drift + two periodic components.

    Parameters
    ----------
    t : np.ndarray
        Time axis in seconds.

    Returns
    -------
    np.ndarray
        The deterministic part of the signal, same shape as ``t``.
    """
    trend = 0.15 * t
    slow = 2.0 * np.sin(2 * np.pi * 1.0 * t)  # 1.0 Hz main component
    fast = 0.6 * np.sin(2 * np.pi * 2.5 * t)  # 2.5 Hz secondary component
    return trend + slow + fast


def _resample(x: np.ndarray, n_out: int) -> np.ndarray:
    """Linearly resample ``x`` to ``n_out`` samples (same duration, new rate)."""
    src = np.linspace(0.0, 1.0, len(x))
    dst = np.linspace(0.0, 1.0, n_out)
    return np.interp(dst, src, x)


def _step_signal(n: int, rng: np.random.Generator) -> np.ndarray:
    """A structurally different signal (piecewise-constant steps + noise)."""
    levels = np.array([0.0, 3.0, -1.0, 1.5])
    steps = np.repeat(levels, int(np.ceil(n / len(levels))))[:n]
    return steps + rng.normal(0.0, 0.15, size=n)


def generate_dataset() -> dict[str, np.ndarray]:
    """Build the fixed set of 1-D signals used by every notebook.

    All variants are derived from a single ``reference`` series so that any
    distance measured against the reference can be attributed to exactly one
    kind of distortion.

    Returns
    -------
    dict[str, np.ndarray]
        Mapping from variant name to a 1-D float array.  ``reference`` is
        always the first key; every other key is one distorted variant:

        ``amplitude_scaled``
            Reference multiplied by :data:`AMPLITUDE_FACTOR`.
        ``resampled``
            Reference stretched to 130 % of its length (different sampling
            rate, same underlying shape).
        ``noisy``
            Reference plus extra Gaussian noise.
        ``phase_shifted``
            The same underlying process, observed :data:`SHIFT` samples later.
        ``reversed``
            Reference read back-to-front.
        ``unrelated``
            A piecewise-constant step signal used as a negative control.
    """
    rng = np.random.default_rng(SEED)

    # Generate a slightly longer trace than needed; `reference` and
    # `phase_shifted` are two overlapping windows of it, so the shift is a real
    # time offset rather than a wrap-around of the same array.
    n_full = N_SAMPLES + SHIFT
    t_full = np.arange(n_full) / FS
    full = _base_signal(t_full) + rng.normal(0.0, BASE_NOISE_STD, size=n_full)

    reference = full[:N_SAMPLES]
    phase_shifted = full[SHIFT:SHIFT + N_SAMPLES]

    return {
        "reference": reference,
        "amplitude_scaled": AMPLITUDE_FACTOR * reference,
        "resampled": _resample(reference, int(N_SAMPLES * RESAMPLE_FACTOR)),
        "noisy": reference + rng.normal(0.0, EXTRA_NOISE_STD, size=N_SAMPLES),
        "phase_shifted": phase_shifted,
        "reversed": reference[::-1].copy(),
        "unrelated": _step_signal(N_SAMPLES, rng),
    }


def variant_names() -> list[str]:
    """Names of all variants except the reference, in a stable order."""
    return [name for name in generate_dataset() if name != "reference"]


if __name__ == "__main__":  # quick sanity check: python data/synthetic.py
    for name, series in generate_dataset().items():
        print(f"{name:>17}  n={len(series):4d}  "
              f"mean={series.mean():+.3f}  std={series.std():.3f}")
