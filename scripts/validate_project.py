"""Validate the portable project without installing dashboard dependencies."""
import csv
import json
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[1]


def main():
    notebooks = sorted((ROOT / "notebooks").glob("*.ipynb"))
    if not notebooks:
        raise ValueError("No notebooks found")
    for path in notebooks:
        notebook = json.loads(path.read_text(encoding="utf-8"))
        if notebook.get("nbformat") != 4 or not isinstance(notebook.get("cells"), list):
            raise ValueError(f"Invalid notebook: {path.name}")

    database = ROOT / "data" / "medicine.db"
    with sqlite3.connect(database.as_uri() + "?mode=ro", uri=True) as connection:
        if connection.execute("PRAGMA quick_check").fetchone()[0] != "ok":
            raise ValueError("SQLite integrity check failed")
        count = connection.execute("SELECT COUNT(*) FROM vw_medicine_details").fetchone()[0]
        if count == 0:
            raise ValueError("Medicine view is empty")

    for name in ("alternatives_per_medicine", "alternatives_per_group", "manufacturer_price_index"):
        path = ROOT / "reports" / "analysis" / f"{name}.csv"
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames or next(reader, None) is None:
                raise ValueError(f"Empty analysis table: {path.name}")
    print(f"Validated {len(notebooks)} notebooks, {count:,} medicines, and 3 analysis tables.")


if __name__ == "__main__":
    main()
