# Twin Coast EDA — Coastal Weather Comparison (Karachi vs. Mumbai)

An end-to-end web scraping, data cleaning, and exploratory climate analysis
project comparing winter coastal weather dynamics between **Karachi, Pakistan**
and **Mumbai, India** using historical hourly observations and 14-day forecast
data (`2025-12-16` through `2026-01-12`).

## Project Structure

- `twin-coast-eda.ipynb` — Unified Jupyter Notebook covering:
  1. **Environment Setup** — Imports, directory creation, and visualization
     styling
  2. **Data Acquisition (Web Scraping)** — Scraping historical hourly tables
     (`#wt-his`) and 14-day forecast tables (`#wt-ext`) from TimeAndDate
     (`RUN_SCRAPER = False` by default to use cached CSVs)
  3. **Data Cleaning & Integration** — Explicit timestamp parsing, numeric
     coercion, deduplication, forward-fill imputation, and exporting
     `dataset/coastal_weather_cleaned.csv`
  4. **Exploratory Data Analysis & Visualizations** — Summary statistics and 6
     publication charts exported to `visualizations/`
  5. **Key Analytical Insights** — Early morning humidity, midday temperature
     and barometric pressure, and rainfall event summaries
- `dataset/`
  - `karachi_raw.csv` — Raw scraped observations for Karachi (`672` rows:
    `658` historic, `14` forecast)
  - `mumbai_raw.csv` — Raw scraped observations for Mumbai (`98` rows:
    `84` historic, `14` forecast)
  - `coastal_weather_cleaned.csv` — Cleaned and combined comparative dataset
    (`770` rows × `10` columns, `0` missing values)
- `visualizations/`
  - `Temperature_Time_Series_Monthly.png`
  - `Temperature_Time_Series_Hourly.png`
  - `Temperature_Time_Series_Daily.png`
  - `Temperature_Distribution.png`
  - `Humidity_Distribution.png`
  - `Wind_Pressure_Comparison.png`
  - `WEATHER_COMPARISON_REPORT.html` — Self-contained HTML report exported from
    the executed notebook
  - `WEATHER_COMPARISON_REPORT.pdf` — Printable PDF version of the weather
    comparison report
- `tests/`
  - `test_project.py` — Automated `unittest` suite verifying configuration
    files, notebook compilation and outputs, dataset invariants, summary
    metrics, and visualization deliverables
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

   - Set `RUN_SCRAPER = True` in cell 4 only if you want to scrape fresh data
     from TimeAndDate instead of using the cached CSVs in `dataset/`.

## Verified Deliverable Metrics Snapshot

Computed directly from `dataset/coastal_weather_cleaned.csv` (`770`
observations across `2025-12-16 00:00:00` to `2026-01-12 12:00:00`):

| Metric | Karachi (`n = 672`) | Mumbai (`n = 98`) |
| --- | :---: | :---: |
| Mean Temperature (°C) | 19.90 | 26.84 |
| Temperature Range (°C) | 13.00 – 32.00 | 24.00 – 30.00 |
| Mean Humidity (%) | 44.09 | 57.38 |
| Early Morning Humidity (5–8 AM, %) | 65.5 | 72.0 |
| Midday Temperature (12–2 PM, °C) | 27.8 | 28.4 |
| Mean Wind Speed (km/h) | 14.66 (median 2.50) | 28.04 (median 30.00) |
| Mean Barometer (mbar) | 1014.23 | 1011.29 |
| Midday Barometer (12–2 PM, mbar) | 1013.3 | 1010.5 |
| Recorded Rainfall Events | 0 | 0 |

## Troubleshooting

- **Pyrefly reports missing site-packages on another machine:** Update
  `python-interpreter-path` and `site-package-path` in `pyrefly.toml` (and
  `python.defaultInterpreterPath` / `ruff.interpreter` in
  `.vscode/settings.json`) to match your local Python `3.14.7` installation
  path.
- **Jupyter shows wrong or stale kernels in VS Code:** Confirm
  `.vscode/settings.json` includes `"jupyter.excludeUserSitePackages": false`
  and reload the VS Code window (`Developer: Reload Window`).
- **Live web scraping fails or returns partial rows:** TimeAndDate may
  rate-limit repeated requests or change HTML markup; keep
  `RUN_SCRAPER = False` to reproduce all analysis and charts deterministically
  from `dataset/`.

## License

This project is licensed under the [MIT License](LICENSE).
