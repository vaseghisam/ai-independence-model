# AI independence — computational companion

Sam Vaseghi · The Quantastic Journal

Code, numerical results, figures and an animation accompanying **Can AI Keep Learning Without Us?—Autonomous Discovery, Direct Observation and Copyright**. The article itself is not included in this repository.

The model explores changing dependence on human intellectual material, AI investigation, human observations and machine observations. It uses illustrative parameters. It is not calibrated to actual AI systems, and model time is not calendar time.

**Package version:** 0.2.1 · **Mathematical model:** 0.2

## View or download the material

- [Six-scenario overview](figures/figure_2_scenarios.png)
- [Standalone Exhibits 7–12](figures/standalone/)
- [Input-removal experiments](figures/figure_3_removal_experiments.png)
- [Sensitivity analysis](figures/figure_4_sensitivity.png)
- [Sensor-handoff animation](figures/animation_sensor_handoff.gif)
- [Model equations and parameters](MODEL.md)
- [Numerical results](data/results.json) and [verification results](data/verification.json)

To download everything, use GitHub's **Code → Download ZIP**. A tagged release, when available, provides a version-specific download.

## Contents

| Location | Contents |
| --- | --- |
| `code/model.py` | Canonical model, six scenario definitions, flow calculations and ODE solver |
| `code/run_all.py` | Full offline reproduction, including the removal experiments, sensitivity grid and animation |
| `code/render_standalone.py` | Standalone Exhibits 7–12, calculated from `model.py` |
| `code/messi_style.py` | Bundled typography and layout helper; no external skill installation is needed |
| `code/write_checksums.py` | SHA-256 manifest generation |
| `data/` | CSV trajectories, plotted samples, sensitivity grid, model parameters, results and verification records |
| `figures/` | Four overview figures as PNG and SVG, plus the GIF animation |
| `figures/standalone/` | Six complete scenario figures as 3200 × 1800 PNGs and editable SVGs |
| `MODEL.md` | Equations, notation, scenario settings and intervention definitions |
| `CITATION.cff` | Citation metadata for this computational companion |
| `SHA256SUMS.txt` | Integrity checksums for the supplied files |

All included visual assets were generated for the model. External photographs and research-paper illustrations used in the article are not included.

## Reproduce all results

Python 3.10 or later is required. From the repository folder, create a virtual environment and install the dependencies. On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python code/run_all.py
```

The final command recreates the numerical data, all ten static figures, the animation and the verification records. It also refreshes the checksum manifest. It writes generated outputs within `data/` and `figures/`; it does not need the article, internet access, external datasets or trained model weights. Installation of dependencies may require internet access.

To regenerate only Exhibits 7–12:

```bash
python code/render_standalone.py
python code/write_checksums.py
```

The supplied environment is recorded in [`data/environment.json`](data/environment.json). Numerical agreement should be assessed with the tolerances below; different graphics-library versions may change image bytes or text layout.

## Figure mapping to the article

| Article exhibit | File |
| --- | --- |
| 5 — Source routes | `figures/figure_1_source_routes.png` |
| 6 — Six scenarios | `figures/figure_2_scenarios.png` |
| 7 — Case A | `figures/standalone/Exhibit_07_Case_A.png` |
| 8 — Case B | `figures/standalone/Exhibit_08_Case_B.png` |
| 9 — Case C | `figures/standalone/Exhibit_09_Case_C.png` |
| 10 — Case D | `figures/standalone/Exhibit_10_Case_D.png` |
| 11 — Case E | `figures/standalone/Exhibit_11_Case_E.png` |
| 12 — Case F | `figures/standalone/Exhibit_12_Case_F.png` |
| 13 — Removal experiments | `figures/figure_3_removal_experiments.png` |
| 14 — Sensitivity analysis | `figures/figure_4_sensitivity.png` |

These numbers follow the article version reviewed on 20 October 2026. If external images are removed and the article's exhibits are renumbered, the case labels and filenames still identify each simulation.

## Verification and limits

The reproduction script checks solver refinement, nonnegative states, resource accounting, the stock-balance identity, zero-input cases and the analytic crossover relation. The sensitivity grid uses a separate vectorised RK4 implementation; five selected grid points are compared against the adaptive solver. The standalone figures use tighter integration and compare their endpoint states with the corresponding baseline runs.

The supplied results reproduce the approximately 52% and 38% final-capability ratios reported for the specified removal experiments. Detailed values and the actual numerical differences are in the JSON records. These checks verify the calculations under the assumptions, not whether those assumptions describe future AI systems.

To check the downloaded files against the supplied manifest on macOS:

```bash
shasum -a 256 -c SHA256SUMS.txt
```

## Citation

Vaseghi, Sam. *AI independence — computational companion*. Version 0.2.1, 2026. Model version 0.2. See `CITATION.cff` for machine-readable metadata. The article should be cited separately when discussing its broader argument.
