"""Automated validation checks for the twin-coast-eda project."""

import json
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent


class TestProjectDeliverables(unittest.TestCase):
    """Verify environment configs, notebook execution, datasets, and charts."""

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
        self.assertEqual(len(code_cells), 11)

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
            "Weather",
            "Wind Speed (km/h)",
            "Wind Direction",
            "Humidity (%)",
            "Barometer (mbar)",
            "Visibility (km)",
            "Data Source",
        ]

        karachi_raw = pd.read_csv(ROOT / "dataset" / "karachi_raw.csv")
        mumbai_raw = pd.read_csv(ROOT / "dataset" / "mumbai_raw.csv")
        cleaned = pd.read_csv(ROOT / "dataset" / "coastal_weather_cleaned.csv")

        self.assertEqual(karachi_raw.shape, (672, 10))
        self.assertEqual(mumbai_raw.shape, (98, 10))
        self.assertEqual(cleaned.shape, (770, 10))
        self.assertEqual(list(cleaned.columns), expected_columns)
        self.assertEqual(int(cleaned.isnull().sum().sum()), 0)

        city_counts = cleaned["City"].value_counts().to_dict()
        self.assertEqual(city_counts, {"Karachi": 672, "Mumbai": 98})

        means = cleaned.groupby("City")[["Temperature (°C)", "Humidity (%)", "Barometer (mbar)"]].mean()
        expected_means = {
            ("Karachi", "Temperature (°C)"): 19.90,
            ("Mumbai", "Temperature (°C)"): 26.84,
            ("Karachi", "Humidity (%)"): 44.09,
            ("Mumbai", "Humidity (%)"): 57.38,
            ("Karachi", "Barometer (mbar)"): 1014.23,
            ("Mumbai", "Barometer (mbar)"): 1011.29,
        }
        for (city, column), expected in expected_means.items():
            value = means.at[city, column]
            self.assertIsInstance(value, (int, float))
            assert isinstance(value, (int, float))
            self.assertAlmostEqual(float(value), expected, places=2)

    def test_visualizations_and_reports_exist_and_valid(self) -> None:
        png_files = [
            "Temperature_Time_Series_Monthly.png",
            "Temperature_Time_Series_Hourly.png",
            "Temperature_Time_Series_Daily.png",
            "Temperature_Distribution.png",
            "Humidity_Distribution.png",
            "Wind_Pressure_Comparison.png",
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
