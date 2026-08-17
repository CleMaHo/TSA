# TSA — comparing time-series similarity measures

Four approaches to measuring the similarity of two 1-D sensor signals, implemented from
scratch and demonstrated on one shared, seeded synthetic dataset:

| Notebook | Method | Idea in one line |
| --- | --- | --- |
| [01_dtw.ipynb](notebooks/01_dtw.ipynb) | Dynamic Time Warping | cheapest monotone alignment, summing real magnitude differences |
| [02_edr.ipynb](notebooks/02_edr.ipynb) | Edit Distance on Real sequences | edit distance with an `eps` tolerance band instead of character equality |
| [03_erp.ipynb](notebooks/03_erp.ipynb) | Edit distance with Real Penalty | edit distance with real-valued costs against a gap element `g` — a true metric |
| [04_statistical_features.ipynb](notebooks/04_statistical_features.ipynb) | Statistical features | summarise each series into 12 features, compare in standardized feature space |
| [05_comparison.ipynb](notebooks/05_comparison.ipynb) | — | all four side by side, as a table and a grouped bar chart |

## Layout

```
.
├── requirements.txt
├── data/
│   └── synthetic.py     # the shared, seeded dataset used by every notebook
├── notebooks/
│   ├── 01_dtw.ipynb
│   ├── 02_edr.ipynb
│   ├── 03_erp.ipynb
│   ├── 04_statistical_features.ipynb
│   └── 05_comparison.ipynb
└── utils/
    ├── distances.py     # finished versions of all four measures (used by notebook 05)
    └── plotting.py      # shared matplotlib helpers
```

Every notebook derives its algorithm from scratch with a numpy DP matrix; `utils/distances.py`
holds the same implementations in finished form so notebook 05 can import rather than
copy them. All notebooks load the identical dataset from `data/synthetic.py`
(`reference` plus six controlled distortions: amplitude-scaled, resampled, noisy,
phase-shifted, reversed, and one unrelated negative control), so the four rankings are
directly comparable.

## Running

```bash
python -m venv .venv
.venv/Scripts/activate          # Windows;  source .venv/bin/activate elsewhere
pip install -r requirements.txt
jupyter lab                     # or open the notebooks in VS Code
```

Notebooks are meant to be run top to bottom in order. They add the project root to
`sys.path` themselves, so `from data.synthetic import generate_dataset` works from
inside `notebooks/`.
