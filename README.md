# Twin Coast EDA — Coastal Weather Comparison & Forecasting

An end-to-end data engineering, exploratory climate analysis, and machine
learning project comparing 4 years of hourly coastal weather (`2022-01-01`
through `2025-12-31`, `70,128` observations) between **Karachi, Pakistan** and
**Mumbai, India** using the **Open-Meteo Historical Weather API (ERA5)**.

## Project Structure

- `twin-coast-eda.ipynb` — Unified Jupyter Notebook covering:
  1. **Environment Setup** — Dependencies, output directories (`dataset/`,
     `model/`, `visualizations/`), and plotting configuration
  2. **Data Acquisition (Open-Meteo ERA5 API)** — Fetching 4 years of hourly
     weather observations (`35,064` rows/city; `RUN_FETCH = False` by default
     to use cached CSVs)
  3. **Data Cleaning & Integration** — Explicit ISO-8601 timestamp parsing,
     numeric coercion, deduplication, forward-fill imputation, and exporting
     `dataset/coastal_weather_cleaned.csv`
  4. **Exploratory Data Analysis & Visualizations** — Multi-year summary
     statistics and 6 climate charts exported to `visualizations/`
  5. **Key Analytical Insights** — Early morning humidity, midday temperature
     and pressure, and 4-year monsoon rainfall totals
  6. **Predictive Modeling (+6h Temperature Forecasting)** — Causal lag,
     rolling, and cyclical feature engineering (`21` predictors), chronological
     `2022–2024` train / `2025` unseen test split, model benchmarking,
     evaluation chart (`Model_Evaluation.png`), and saving
     `model/coastal_weather_temp_forecaster.pkl`
- `dataset/`
  - `karachi_raw.csv` — 4-year Open-Meteo hourly archive for Karachi
    (`35,064` rows × `11` columns)
  - `mumbai_raw.csv` — 4-year Open-Meteo hourly archive for Mumbai
    (`35,064` rows × `11` columns)
  - `coastal_weather_cleaned.csv` — Cleaned and combined multi-year dataset
    (`70,128` rows × `11` columns, `0` missing values)
- `model/`
  - `coastal_weather_temp_forecaster.pkl` — Serialized `HistGradientBoosting`
    +6-hour temperature forecaster bundle (`joblib`, `0.44 MB`) with feature
    contract and verified 2025 holdout metrics
- `visualizations/`
  - `Temperature_Time_Series_Monthly.png`
  - `Temperature_Time_Series_Hourly.png`
  - `Temperature_Time_Series_Daily.png`
  - `Temperature_Distribution.png`
  - `Humidity_Distribution.png`
  - `Wind_Pressure_Comparison.png`
  - `Model_Evaluation.png`
  - `WEATHER_COMPARISON_REPORT.html` — Self-contained HTML report exported from
    the executed notebook
  - `WEATHER_COMPARISON_REPORT.pdf` — Printable PDF version of the full report
- `tests/`
  - `test_project.py` — Automated `unittest` suite verifying configuration
    files, notebook compilation/execution, dataset invariants, serialized model
    inference, and visualization deliverables
- `.github/workflows/ci.yml` — Continuous integration workflow running Ruff,
  Pyrefly, and `unittest` on Python `3.14`
- `.python-version`, `pyproject.toml`, `requirements.txt`, `pyrefly.toml` —
  Global Python `3.14.7` and static-analysis configuration
- `.vscode/settings.json`, `.vscode/extensions.json` — Pre-configured VS Code
  workspace settings for system Python `3.14.7`, Jupyter, Ruff, and Pyrefly

## Python & IDE Configuration

This repository is configured to run directly on your **global Python
`3.14.7`** interpreter (no `.venv` required):

- **`.python-version`**: Pins Python `3.14.7`.
- **`pyproject.toml`**: Declares `requires-python = ">=3.14.7,<3.15"`, core
  runtime dependencies, optional `[project.optional-dependencies].dev` typing
  stubs, and `[tool.ruff]` lint rules.
- **`requirements.txt`**: Freezes verified dependencies with flexible version
  bounds (`>=installed,<next_major` for SemVer packages and `>=installed` for
  CalVer stub packages).
- **`pyrefly.toml`**: Configures `meta.pyrefly` across `**/*.py*` and
  `**/*.ipynb` using the global Python `3.14.7` interpreter and
  `site-packages`.
- **`.vscode/settings.json` & `.vscode/extensions.json`**: Configures VS Code
  to use the system Python `3.14.7` interpreter (`ms-python.python:system`),
  bundled Pyrefly (`python.languageServer: "None"`,
  `python.pyrefly.syncNotebooks: true`), Ruff, Jupyter kernel filtering, and
  recommended extensions (`ms-python.python`, `ms-python.vscode-python-envs`,
  `meta.pyrefly`, `ms-toolsai.jupyter`, `charliermarsh.ruff`,
  `davidanson.vscode-markdownlint`).

## First-Time Setup & Run Checklist

1. **Verify Python `3.14.7` is active:**

   ```bash
   python --version
   ```

2. **Install runtime and typing-stub dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run static checks and automated tests:**

   ```bash
   ruff check .
   pyrefly check
   python -m unittest discover -s tests -v
   ```

4. **Open and run the notebook:**
   - In **VS Code**: Open `twin-coast-eda.ipynb`, select the **Python 3.14.7**
     kernel, and click **Run All**.
   - Or launch classic Jupyter Notebook from the terminal:

     ```bash
     pip install notebook
     jupyter notebook twin-coast-eda.ipynb
     ```

   - Set `RUN_FETCH = True` in cell 4 only if you want to re-fetch live data
     from the Open-Meteo Historical Weather API instead of using `dataset/`.

## Verified Deliverable Metrics Snapshot

### 4-Year Climate Summary (`2022-01-01` to `2025-12-31`, `n = 70,128`)

| Metric | Karachi (`n = 35,064`) | Mumbai (`n = 35,064`) |
| --- | :---: | :---: |
| Mean Temperature (°C) | 26.36 | 26.99 |
| Temperature Range (°C) | 8.90 – 41.60 | 14.30 – 41.30 |
| Mean Humidity (%) | 67.41 | 71.02 |
| Early Morning Humidity (5–8 AM, %) | 78.1 | 78.4 |
| Midday Temperature (12–2 PM, °C) | 30.1 | 30.7 |
| Mean Wind Speed (km/h) | 15.45 (median 14.30) | 11.34 (median 10.30) |
| Mean Barometer (mbar) | 1007.81 | 1008.28 |
| Recorded Rain Hours | 2,473 | 9,892 |
| Cumulative Rainfall (mm) | 1,555.3 | 9,891.2 |

### +6-Hour Temperature Forecasting (`2025` Unseen Holdout, `n = 17,508`)

| Model | MAE (°C) | RMSE (°C) | R² |
| --- | :---: | :---: | :---: |
| Persistence Baseline (`T_t`) | 3.1892 | 4.1348 | -0.0657 |
| Ridge Regression | 1.1558 | 1.5073 | 0.8584 |
| Random Forest (`max_depth=14`) | 0.6877 | 0.9632 | 0.9422 |
| **HistGradientBoosting** (Saved) | **0.6516** | **0.9064** | **0.9488** |

Per-city 2025 holdout metrics for `model/coastal_weather_temp_forecaster.pkl`:
Karachi `MAE = 0.6381°C` (`R² = 0.9619`) and Mumbai `MAE = 0.6651°C`
(`R² = 0.9195`); serialized model reload parity `max_diff = 0.000000`.

## Troubleshooting

- **Pyrefly reports missing site-packages on another machine:** Update
  `python-interpreter-path` and `site-package-path` in `pyrefly.toml` (and
  `python.defaultInterpreterPath` / `ruff.interpreter` in
  `.vscode/settings.json`) to match your local Python `3.14.7` installation
  path.
- **Jupyter shows wrong or stale kernels in VS Code:** Confirm
  `.vscode/settings.json` includes `"jupyter.excludeUserSitePackages": false`
  and reload the VS Code window (`Developer: Reload Window`).
- **Live Open-Meteo fetch times out or is offline:** Keep `RUN_FETCH = False`
  to reproduce all data cleaning, EDA charts, model training, and reports
  deterministically from `dataset/`.

## License

This project is licensed under the [MIT License](LICENSE).
