"""Small plotting helpers shared by the similarity notebooks.

Nothing here is algorithm-specific: the notebooks pass in the DP matrices and
paths they computed themselves, these functions only take care of the
matplotlib boilerplate so the notebook cells stay short and readable.
"""

from __future__ import annotations

from typing import Iterable, Sequence

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def plot_dataset(dataset: dict[str, np.ndarray], ncols: int = 2) -> None:
    """Plot every series of the dataset in its own subplot.

    Parameters
    ----------
    dataset : dict[str, np.ndarray]
        Output of ``generate_dataset()``.
    ncols : int
        Number of subplot columns.
    """
    names = list(dataset)
    nrows = int(np.ceil(len(names) / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(11, 2.0 * nrows), sharex=True)
    for ax, name in zip(axes.ravel(), names):
        ax.plot(dataset[name], lw=1.0, color="tab:blue" if name == "reference" else "tab:gray")
        ax.set_title(f"{name}  (n={len(dataset[name])})", fontsize=9)
        ax.grid(alpha=0.3)
    for ax in axes.ravel()[len(names):]:  # hide unused axes
        ax.axis("off")
    fig.supxlabel("sample index")
    fig.tight_layout()
    plt.show()


def plot_pair(x: np.ndarray, y: np.ndarray, labels: Sequence[str] = ("x", "y"),
              title: str = "") -> None:
    """Overlay two series in a single axes."""
    plt.figure(figsize=(11, 3))
    plt.plot(x, lw=1.2, label=labels[0])
    plt.plot(y, lw=1.2, alpha=0.8, label=labels[1])
    plt.title(title or f"{labels[0]} vs. {labels[1]}")
    plt.xlabel("sample index")
    plt.ylabel("value")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()


def plot_cost_matrix(cost: np.ndarray,
                     path: Iterable[tuple[int, int]] | None = None,
                     title: str = "DP cost matrix",
                     xlabel: str = "y index (j)",
                     ylabel: str = "x index (i)",
                     cbar_label: str = "accumulated cost",
                     cmap: str = "viridis",
                     ax: "plt.Axes | None" = None) -> None:
    """Heatmap of a DP matrix with the optimal path drawn on top.

    Parameters
    ----------
    cost : np.ndarray
        The (n, m) accumulated-cost matrix (without the padding row/column).
    path : iterable of (i, j), optional
        Optimal alignment path in matrix coordinates.
    title, xlabel, ylabel, cbar_label, cmap
        Cosmetic options; kept identical across notebooks 1-3 so the three
        heatmaps can be compared at a glance.
    ax : matplotlib Axes, optional
        Draw into an existing axes instead of creating a new figure.  Used by
        notebook 05 to put several cost matrices side by side; the caller is
        then responsible for ``plt.show()``.
    """
    standalone = ax is None
    if standalone:
        _, ax = plt.subplots(figsize=(6.5, 5.5))

    im = ax.imshow(cost, origin="lower", aspect="auto", cmap=cmap, interpolation="nearest")
    ax.figure.colorbar(im, ax=ax, label=cbar_label)
    if path is not None:
        path = np.asarray(list(path))
        ax.plot(path[:, 1], path[:, 0], color="red", lw=1.5, label="optimal path")
        ax.legend(loc="upper left")
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    if standalone:
        ax.figure.tight_layout()
        plt.show()


def plot_alignment(x: np.ndarray, y: np.ndarray,
                   path: Sequence[tuple[int, int]],
                   labels: Sequence[str] = ("x", "y"),
                   offset: float = 6.0,
                   every: int = 5,
                   title: str = "alignment") -> None:
    """Draw two series stacked vertically with connecting alignment lines.

    Parameters
    ----------
    offset : float
        Vertical distance between the two curves.
    every : int
        Draw only every ``every``-th connection to keep the plot readable.
    """
    plt.figure(figsize=(11, 4))
    plt.plot(x + offset, lw=1.2, label=f"{labels[0]} (+{offset:g})")
    plt.plot(y, lw=1.2, label=labels[1])
    for i, j in list(path)[::every]:
        plt.plot([i, j], [x[i] + offset, y[j]], color="gray", lw=0.4, alpha=0.6)
    plt.title(title)
    plt.xlabel("sample index")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()


def plot_distance_bars(table: pd.DataFrame, title: str = "distance to reference",
                       ylabel: str = "distance") -> None:
    """Grouped bar chart: one group per variant (row), one bar per method (column)."""
    ax = table.plot(kind="bar", figsize=(11, 4.5), width=0.8, edgecolor="black", linewidth=0.4)
    ax.set_title(title)
    ax.set_xlabel("variant")
    ax.set_ylabel(ylabel)
    ax.grid(axis="y", alpha=0.3)
    ax.legend(title="method")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    plt.show()
