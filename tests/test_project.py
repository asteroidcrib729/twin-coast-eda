"""Automated validation checks for the twin-coast-eda project."""

import json
import unittest
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, r2_score

ROOT = Path(__file__).resolve().parent.parent


class TestProjectDeliverables(unittest.TestCase):
    """Verify environment configs, notebook execution, datasets, model, and charts."""

    def test_required_config_and_repo_files_exist(self) -> None:
        required_files = [
            ".python-version",
            "pyproject.toml",
            "requirements.txt",
            "pyrefly.toml",
            ".gitignore",
            ".gitattributes",
            "LICENSE",
            "README.md",
            ".vscode/settings.json",
            ".vscode/extensions.json",
            ".github/workflows/ci.yml",
            "twin-coast-eda.ipynb",
            "model/coastal_weather_temp_forecaster.pkl",
        ]
        for rel_path in required_files:
            path = ROOT / rel_path
            self.assertTrue(path.is_file(), f"Missing required file: {rel_path}")
            self.assertGreater(path.stat().st_size, 0, f"Empty file: {rel_path}")

        self.assertEqual((ROOT / ".python-version").read_text(encoding="utf-8").strip(), "3.14.7")
        license_first_line = (ROOT / "LICENSE").read_text(encoding="utf-8").splitlines()[0]
        self.assertEqual(license_first_line, "# MIT License")

    def test_notebook_metadata_syntax_and_outputs(self) -> None:
        nb_path = ROOT / "twin-coast-eda.ipynb"
        nb = json.loads(nb_path.read_text(encoding="utf-8"))

        self.assertEqual(nb["metadata"]["language_info"]["version"], "3.14.7")
        code_cells = [c for c in nb["cells"] if c.get("cell_type") == "code"]
        self.assertEqual(len(code_cells), 12)

        for index, cell in enumerate(code_cells, start=1):
            source = "".join(cell.get("source", []))
            compile(source, f"twin-coast-eda.ipynb#code-cell-{index}", "exec")
            self.assertIsNotNone(
                cell.get("execution_count"),
                f"Code cell {index} has not been executed.",
            )
            for output in cell.get("outputs", []):
                self.assertNotEqual(
                    output.get("output_type"),
                    "error",
                    f"Code cell {index} contains error output: {output}",
                )

    def test_datasets_and_summary_metrics(self) -> None:
        expected_columns = [
            "Date & Time",
            "City",
            "Temperature (°C)",
            "Weather Code",
            "Weather",
            "Wind Speed (km/h)",
            "Wind Direction (°)",
            "Humidity (%)",
            "Barometer (mbar)",
            "Precipitation (mm)",
            "Data Source",
        ]

        karachi_raw = pd.read_csv(ROOT / "dataset" / "karachi_raw.csv")
        mumbai_raw = pd.read_csv(ROOT / "dataset" / "mumbai_raw.csv")
        cleaned = pd.read_csv(ROOT / "dataset" / "coastal_weather_cleaned.csv")

        self.assertEqual(karachi_raw.shape, (35064, 11))
        self.assertEqual(mumbai_raw.shape, (35064, 11))
        self.assertEqual(cleaned.shape, (70128, 11))
        self.assertEqual(list(cleaned.columns), expected_columns)
        self.assertEqual(int(cleaned.isnull().sum().sum()), 0)

        city_counts = cleaned["City"].value_counts().to_dict()
        self.assertEqual(city_counts, {"Karachi": 35064, "Mumbai": 35064})

        means = cleaned.groupby("City")[["Temperature (°C)", "Humidity (%)", "Barometer (mbar)"]].mean()
        expected_means = {
            ("Karachi", "Temperature (°C)"): 26.36,
            ("Mumbai", "Temperature (°C)"): 26.99,
            ("Karachi", "Humidity (%)"): 67.41,
            ("Mumbai", "Humidity (%)"): 71.02,
            ("Karachi", "Barometer (mbar)"): 1007.81,
            ("Mumbai", "Barometer (mbar)"): 1008.28,
        }
        for (city, column), expected in expected_means.items():
            value = means.at[city, column]
            self.assertIsInstance(value, (int, float))
            assert isinstance(value, (int, float))
            self.assertAlmostEqual(float(value), expected, places=2)

    def test_model_artifact_loads_and_predicts(self) -> None:
        artifact = joblib.load(ROOT / "model" / "coastal_weather_temp_forecaster.pkl")
        self.assertEqual(artifact["model_name"], "HistGradientBoosting")
        self.assertEqual(artifact["horizon_hours"], 6)
        self.assertEqual(artifact["target_column"], "Target_Temp_6h")
        self.assertEqual(len(artifact["feature_columns"]), 21)
        self.assertEqual(artifact["train_rows"], 52560)
        self.assertEqual(artifact["test_rows"], 17508)
        self.assertAlmostEqual(float(artifact["test_metrics"]["mae"]), 0.6516, places=4)
        self.assertAlmostEqual(float(artifact["test_metrics"]["r2"]), 0.9488, places=4)

        df = pd.read_csv(ROOT / "dataset" / "coastal_weather_cleaned.csv")
        df["Date & Time"] = pd.to_datetime(df["Date & Time"], format="%Y-%m-%d %H:%M:%S")
        df["Hour"] = df["Date & Time"].dt.hour
        df["DayOfYear"] = df["Date & Time"].dt.day_of_year

        frames = []
        for _city, grp in df.groupby("City", sort=False):
            g = grp.sort_values("Date & Time").copy()
            g["Temp_Lag_1h"] = g["Temperature (°C)"].shift(1)
            g["Temp_Lag_3h"] = g["Temperature (°C)"].shift(3)
            g["Temp_Lag_6h"] = g["Temperature (°C)"].shift(6)
            g["Temp_Lag_24h"] = g["Temperature (°C)"].shift(24)
            g["Temp_Diff_1h"] = g["Temperature (°C)"] - g["Temp_Lag_1h"]
            g["Temp_Diff_3h"] = g["Temperature (°C)"] - g["Temp_Lag_3h"]
            g["Pressure_Diff_3h"] = g["Barometer (mbar)"] - g["Barometer (mbar)"].shift(3)
            g["Humidity_Diff_3h"] = g["Humidity (%)"] - g["Humidity (%)"].shift(3)
            g["Temp_RollMean_24h"] = g["Temperature (°C)"].rolling(24).mean()
            g["Temp_RollStd_24h"] = g["Temperature (°C)"].rolling(24).std()
            g["Target_Temp_6h"] = g["Temperature (°C)"].shift(-6)
            frames.append(g)

        ml_df = pd.concat(frames, ignore_index=True).dropna().reset_index(drop=True)
        ml_df["City_Is_Mumbai"] = (ml_df["City"] == "Mumbai").astype(int)
        ml_df["Hour_Sin"] = np.sin(2 * np.pi * ml_df["Hour"] / 24.0)
        ml_df["Hour_Cos"] = np.cos(2 * np.pi * ml_df["Hour"] / 24.0)
        ml_df["DayOfYear_Sin"] = np.sin(2 * np.pi * ml_df["DayOfYear"] / 365.25)
        ml_df["DayOfYear_Cos"] = np.cos(2 * np.pi * ml_df["DayOfYear"] / 365.25)

        test_df = ml_df.loc[ml_df["Date & Time"] >= pd.Timestamp("2025-01-01 00:00:00")]
        preds = np.asarray(artifact["estimator"].predict(test_df[artifact["feature_columns"]]), dtype=float)
        self.assertEqual(len(preds), 17508)
        self.assertTrue(np.all(np.isfinite(preds)))
        self.assertAlmostEqual(float(mean_absolute_error(test_df["Target_Temp_6h"], preds)), 0.6516, places=4)
        self.assertAlmostEqual(float(r2_score(test_df["Target_Temp_6h"], preds)), 0.9488, places=4)

    def test_visualizations_and_reports_exist_and_valid(self) -> None:
        png_files = [
            "Temperature_Time_Series_Monthly.png",
            "Temperature_Time_Series_Hourly.png",
            "Temperature_Time_Series_Daily.png",
            "Temperature_Distribution.png",
            "Humidity_Distribution.png",
            "Wind_Pressure_Comparison.png",
            "Model_Evaluation.png",
        ]
        for filename in png_files:
            path = ROOT / "visualizations" / filename
            self.assertTrue(path.is_file(), f"Missing visualization: {filename}")
            data = path.read_bytes()
            self.assertTrue(data.startswith(b"\x89PNG\r\n\x1a\n"), f"Invalid PNG header: {filename}")

        html_path = ROOT / "visualizations" / "WEATHER_COMPARISON_REPORT.html"
        pdf_path = ROOT / "visualizations" / "WEATHER_COMPARISON_REPORT.pdf"
        self.assertTrue(html_path.is_file(), "Missing HTML report")
        self.assertTrue(pdf_path.is_file(), "Missing PDF report")

        html_text = html_path.read_text(encoding="utf-8")
        self.assertIn("<!DOCTYPE html>", html_text)
        self.assertIn("data:image/png;base64,", html_text)
        self.assertTrue(pdf_path.read_bytes().startswith(b"%PDF-"), "Invalid PDF header")


if __name__ == "__main__":
    unittest.main()
