"""Loading helpers for the intimeData_*.mat recordings.

File layout (MAT-file v5, one struct `intimeData` per file):

    intimeData
      t          float64 (N,)            time vector, 1 ms steps
      achsen     object  (6,)            struct array -> one entry per axis
        [i].trajectory  q, dq, ddq, q_add, dq_add, ddq_add
        [i].command     q, dq, tau
        [i].state       q, dq, theta, dtheta, tau, e_q, phi,
                        dq_est, tau_r_est, tau_ext_est
        [i].dummy
      lda        struct                  extra drive, same command/state pattern
        command  torque, torque_add
        state    torque, dq

Not every channel is recorded.  Unlogged ones are written as all-zero uint8
(or int16) placeholders of full length, logged ones are float64 -- that dtype
is the only reliable way to tell them apart, so `_is_logged` filters on it.
Axes 3..5 carry a reduced field set (no command struct, state only theta/tau).
The derived channels `state.dq` / `state.dtheta` are one sample shorter than
`t`; `to_frame` pads them with NaN.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import scipy.io


def load_mat(path):
    """Load one .mat file and return its `intimeData` struct."""
    mat = scipy.io.loadmat(path, squeeze_me=True, struct_as_record=False)
    return mat["intimeData"]


def _is_logged(v):
    """True for channels that actually hold measurements (see module docstring)."""
    return isinstance(v, np.ndarray) and v.dtype.kind == "f" and v.size > 0


def _struct_to_dict(s, drop_empty=True):
    """Flatten one struct (trajectory/command/state) into {field: array}."""
    if not hasattr(s, "_fieldnames"):          # empty struct -> 0-element array
        return {}
    out = {}
    for f in s._fieldnames:
        v = getattr(s, f)
        if not drop_empty or _is_logged(v):
            out[f] = v
    return out


def axis_to_dict(axis, drop_empty=True):
    """One axis -> {"trajectory": {...}, "command": {...}, "state": {...}}."""
    out = {}
    for grp in ("trajectory", "command", "state"):
        if grp in axis._fieldnames:
            fields = _struct_to_dict(getattr(axis, grp), drop_empty)
            if fields or not drop_empty:
                out[grp] = fields
    return out


def get_axis_data(path_to_data_dir, pattern="*.mat", drop_empty=True):
    """Read every .mat file in a directory.

    Returns {file_stem: {"t": t, "axes": {i: {group: {field: array}}},
                         "lda": {group: {field: array}}}}.
    With drop_empty=True only recorded channels appear, so the keys differ
    between files and axes -- check with `.keys()` instead of assuming.
    """
    data = {}
    for path in sorted(Path(path_to_data_dir).glob(pattern)):
        d = load_mat(path)
        data[path.stem] = {
            "t": d.t,
            "axes": {i: axis_to_dict(a, drop_empty)
                     for i, a in enumerate(np.atleast_1d(d.achsen))},
            "lda": {grp: _struct_to_dict(getattr(d.lda, grp), drop_empty)
                    for grp in d.lda._fieldnames
                    if hasattr(getattr(d.lda, grp), "_fieldnames")},
        }
    return data


def to_frame(record, axis_index):
    """One axis of one record -> DataFrame indexed by t, columns "group.field"."""
    import pandas as pd

    t = record["t"]
    cols = {f"{grp}.{f}": np.pad(v, (0, len(t) - len(v)), constant_values=np.nan)
            for grp, fields in record["axes"][axis_index].items()
            for f, v in fields.items()}
    return pd.DataFrame(cols, index=pd.Index(t, name="t"))


def describe(path):
    """Print the full tree of one file, marking unrecorded channels."""
    d = load_mat(path)
    print(f"t: {d.t.shape} {d.t.dtype}  [{d.t[0]} .. {d.t[-1]}] s")
    for i, a in enumerate(np.atleast_1d(d.achsen)):
        print(f"achsen[{i}]  fields={a._fieldnames}")
        for grp in a._fieldnames:
            g = getattr(a, grp)
            if not hasattr(g, "_fieldnames"):
                continue
            for f in g._fieldnames:
                v = getattr(g, f)
                mark = "" if _is_logged(v) else "   <- not recorded"
                print(f"    {grp}.{f:<12s} {str(v.dtype):<8s} n={v.size}{mark}")


if __name__ == "__main__":
    describe(Path(__file__).parent / "mat-files" / "intimeData_1.mat")


# --- Extraction for the similarity notebooks -------------------------------

DEFAULT_DIR = Path(__file__).parent / "mat-files"
DEFAULT_FILES = ("intimeData_7", "intimeData_8")
DEFAULT_AXIS = 2
DEFAULT_CHANNELS = ("q", "tau", "dq")


def get_state_series(
    files: tuple[str, ...] = DEFAULT_FILES,
    channels: tuple[str, ...] = DEFAULT_CHANNELS,
    axis: int = DEFAULT_AXIS,
    group: str = "state",
    data_dir=DEFAULT_DIR,
    step: int = 1,
) -> dict[str, dict[str, np.ndarray]]:
    """Extract one axis' signals from several recordings, ready for DTW/EDR/ERP.

    Counterpart to :func:`data.synthetic.generate_dataset`: where that builds
    synthetic variants of one reference, this pulls comparable real series out
    of different measurement files.

    Parameters
    ----------
    files : tuple of str
        File names, with or without the ``.mat`` suffix.
    channels : tuple of str
        Field names inside the chosen struct, e.g. ``("q", "tau", "dq")``.
    axis : int
        Index into ``intimeData.achsen`` (0..5).
    group : str
        Which struct to read: ``"state"``, ``"trajectory"`` or ``"command"``.
    data_dir : path
        Directory holding the .mat files.
    step : int
        Decimation factor.  The recordings are sampled at 1 kHz, so a DP-matrix
        method (O(n*m) memory) needs ``step=10`` or more to stay tractable.

    Returns
    -------
    dict
        ``{file_stem: {"t": time, <channel>: series, ...}}``.  Within one file
        every array has the same length and shares that file's ``"t"``, so any
        pair of series can go straight into a distance function.  Lengths
        differ *between* files -- that is what the elastic measures handle.

    Raises
    ------
    KeyError
        If a requested channel was not recorded in one of the files (the
        message lists what is available there).
    """
    out = {}
    for name in files:
        path = Path(data_dir) / (name if name.endswith(".mat") else f"{name}.mat")
        d = load_mat(path)
        fields = _struct_to_dict(getattr(np.atleast_1d(d.achsen)[axis], group))

        missing = [c for c in channels if c not in fields]
        if missing:
            raise KeyError(
                f"{path.name}: axis {axis} {group} has no recorded channel(s) "
                f"{missing}; available: {sorted(fields)}"
            )

        # `dq` and `dtheta` are derived by differentiation and are one sample
        # shorter, so cut every array (and t) to the shortest one.
        n = min([len(d.t)] + [len(fields[c]) for c in channels])
        out[path.stem] = {"t": d.t[:n:step],
                          **{c: fields[c][:n:step] for c in channels}}
    return out


def get_series_pair(
    channel: str = "tau",
    files: tuple[str, str] = DEFAULT_FILES,
    **kwargs,
) -> tuple[np.ndarray, np.ndarray]:
    """The same channel from two files as a plain ``(x_a, x_b)`` pair.

    Convenience wrapper around :func:`get_state_series` for the notebooks,
    which call e.g. ``dtw_distance(x_a, x_b)``.  Extra keyword arguments
    (``axis``, ``group``, ``step``, ``data_dir``) are passed through.
    """
    data = get_state_series(files=files, channels=(channel,), **kwargs)
    a, b = (data[Path(f).stem] for f in files)
    return a[channel], b[channel]
