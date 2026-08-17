"""Reference implementations of the four similarity measures.

Notebooks 01-04 each derive their algorithm from scratch, step by step — that is
the point of those notebooks.  This module collects the finished versions of the
same functions so that the final comparison (``notebooks/05_comparison.ipynb``)
can import them instead of copying code between notebooks.  If you change an
algorithm in a notebook, mirror the change here.

All four functions take two 1-D float arrays and return a single float.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

# --------------------------------------------------------------------------- #
# 01 — Dynamic Time Warping
# --------------------------------------------------------------------------- #


def dtw_cost_matrix(x: np.ndarray, y: np.ndarray, local_cost: str = "abs") -> np.ndarray:
    """Accumulated DTW cost matrix, shape ``(len(x) + 1, len(y) + 1)``.

    ``local_cost`` selects ``|x_i - y_j|`` ("abs") or ``(x_i - y_j) ** 2``
    ("squared", the convention of the `dtaidistance` package).
    """
    n, m = len(x), len(y)
    diff = x[:, None] - y[None, :]
    d = np.abs(diff) if local_cost == "abs" else diff ** 2

    D = np.full((n + 1, m + 1), np.inf)
    D[0, 0] = 0.0
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            D[i, j] = d[i - 1, j - 1] + min(D[i - 1, j], D[i, j - 1], D[i - 1, j - 1])
    return D


def dtw_distance(x: np.ndarray, y: np.ndarray, local_cost: str = "abs") -> float:
    """DTW distance (square-rooted for the squared local cost)."""
    total = dtw_cost_matrix(x, y, local_cost)[-1, -1]
    return float(np.sqrt(total) if local_cost == "squared" else total)


# --------------------------------------------------------------------------- #
# 02 — Edit Distance on Real sequences
# --------------------------------------------------------------------------- #


def edr_cost_matrix(x: np.ndarray, y: np.ndarray, eps: float) -> np.ndarray:
    """Accumulated EDR cost matrix, shape ``(len(x) + 1, len(y) + 1)``.

    Two samples count as equal when ``|x_i - y_j| <= eps``; every edit
    (insert / delete / substitute) costs exactly 1.
    """
    n, m = len(x), len(y)
    match = (np.abs(x[:, None] - y[None, :]) <= eps).astype(float)

    D = np.zeros((n + 1, m + 1))
    D[:, 0] = np.arange(n + 1)  # delete all remaining samples of x
    D[0, :] = np.arange(m + 1)  # insert all remaining samples of y
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            sub = 0.0 if match[i - 1, j - 1] else 1.0
            D[i, j] = min(D[i - 1, j - 1] + sub, D[i - 1, j] + 1.0, D[i, j - 1] + 1.0)
    return D


def edr_distance(x: np.ndarray, y: np.ndarray, eps: float) -> float:
    """EDR distance: number of edits needed to make the two series match."""
    return float(edr_cost_matrix(x, y, eps)[-1, -1])


# --------------------------------------------------------------------------- #
# 03 — Edit distance with Real Penalty
# --------------------------------------------------------------------------- #


def erp_cost_matrix(x: np.ndarray, y: np.ndarray, g: float = 0.0) -> np.ndarray:
    """Accumulated ERP cost matrix, shape ``(len(x) + 1, len(y) + 1)``.

    Matches cost ``|x_i - y_j|``; a gap costs the distance of the unmatched
    sample to the constant reference value ``g``.
    """
    n, m = len(x), len(y)
    match = np.abs(x[:, None] - y[None, :])
    gap_x = np.abs(x - g)
    gap_y = np.abs(y - g)

    D = np.zeros((n + 1, m + 1))
    D[1:, 0] = np.cumsum(gap_x)  # x aligned against nothing but gaps
    D[0, 1:] = np.cumsum(gap_y)
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            D[i, j] = min(D[i - 1, j - 1] + match[i - 1, j - 1],
                          D[i - 1, j] + gap_x[i - 1],
                          D[i, j - 1] + gap_y[j - 1])
    return D


def erp_distance(x: np.ndarray, y: np.ndarray, g: float = 0.0) -> float:
    """ERP distance between ``x`` and ``y`` (a true metric for a fixed ``g``)."""
    return float(erp_cost_matrix(x, y, g)[-1, -1])


# --------------------------------------------------------------------------- #
# 04 — Statistical features
# --------------------------------------------------------------------------- #

FEATURE_NAMES = ["mean", "std", "min", "max", "skewness", "kurtosis",
                 "zero_crossing_rate", "dominant_freq", "spectral_energy",
                 "acf_1", "acf_2", "acf_3"]


def autocorrelation(x: np.ndarray, lag: int) -> float:
    """Sample autocorrelation coefficient of ``x`` at ``lag``."""
    x = x - x.mean()
    denom = np.dot(x, x)
    if denom == 0 or lag >= len(x):
        return 0.0
    return float(np.dot(x[:len(x) - lag], x[lag:]) / denom)


def feature_vector(x: np.ndarray) -> np.ndarray:
    """Feature vector of one series, in the order of :data:`FEATURE_NAMES`.

    Frequencies are expressed in cycles *per sample* (i.e. the sampling rate is
    assumed to be 1), so that the function works on a bare 1-D array.
    """
    centered = x - x.mean()
    spectrum = np.abs(np.fft.rfft(centered)) ** 2
    freqs = np.fft.rfftfreq(len(x), d=1.0)

    return np.array([
        x.mean(),
        x.std(),
        x.min(),
        x.max(),
        stats.skew(x),
        stats.kurtosis(x),
        np.mean(np.signbit(x[:-1]) != np.signbit(x[1:])),  # zero-crossing rate
        freqs[np.argmax(spectrum)],
        spectrum.sum() / len(x),
        autocorrelation(x, 1),
        autocorrelation(x, 2),
        autocorrelation(x, 3),
    ])


def feature_table(dataset: dict[str, np.ndarray]) -> pd.DataFrame:
    """Feature matrix: one row per series, one column per feature."""
    return pd.DataFrame({name: feature_vector(series) for name, series in dataset.items()},
                        index=FEATURE_NAMES).T


def standardize(table: pd.DataFrame) -> pd.DataFrame:
    """Z-score every column; constant columns become all-zero instead of NaN."""
    std = table.std(ddof=0).replace(0.0, 1.0)
    return (table - table.mean()) / std


def feature_distances(dataset: dict[str, np.ndarray],
                      reference_key: str = "reference") -> pd.Series:
    """Euclidean distance in standardized feature space to ``reference_key``."""
    z = standardize(feature_table(dataset))
    ref = z.loc[reference_key]
    return ((z - ref) ** 2).sum(axis=1) ** 0.5
