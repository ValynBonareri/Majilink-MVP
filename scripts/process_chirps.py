import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from pathlib import Path

import rasterio
import numpy as np
import pandas as pd

from config.settings import (
    RAW_CHIRPS_DIR,
    PROCESSED_DIR,
    NAIROBI_LAT,
    NAIROBI_LON,
)


def extract_nairobi_value(file_path):

    with rasterio.open(file_path) as src:

        coordinates = [
            (NAIROBI_LON, NAIROBI_LAT)
        ]

        values = list(
            src.sample(coordinates)
        )

        value = values[0][0]

        if value == src.nodata:

            return np.nan

        return float(value)


def main():

    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


    records = []


    files = sorted(
        RAW_CHIRPS_DIR.glob(
            "chirps-v2.0.*.tif"
        )
    )


    print(
        f"Found {len(files)} CHIRPS files."
    )


    for file in files:

        rainfall = extract_nairobi_value(
            file
        )


        parts = file.stem.split(".")


        year = int(parts[2])

        month = int(parts[3])


        records.append({

            "year": year,

            "month": month,

            "latitude": NAIROBI_LAT,

            "longitude": NAIROBI_LON,

            "rainfall_mm": rainfall,

        })


        print(
            f"{year}-{month:02d}: "
            f"{rainfall:.2f} mm"
        )


    dataframe = pd.DataFrame(
        records
    )


    output_file = (
        PROCESSED_DIR
        / "nairobi_rainfall.csv"
    )


    dataframe.to_csv(
        output_file,
        index=False
    )


    print()
    print(
        f"Saved: {output_file}"
    )


if __name__ == "__main__":
    main()