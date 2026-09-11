
import sys
from pathlib import Path
import gzip
import shutil

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import requests
from tqdm import tqdm

from config.settings import (
    CHIRPS_BASE_URL,
    START_YEAR,
    END_YEAR,
    RAW_CHIRPS_DIR,
)


def download_file(url: str, gz_path: Path):

    if gz_path.exists():
        print(f"Already downloaded: {gz_path.name}")
    else:
        print(f"Downloading: {gz_path.name}")

        response = requests.get(
            url,
            stream=True,
            timeout=120
        )

        response.raise_for_status()

        total_size = int(
            response.headers.get("content-length", 0)
        )

        with open(gz_path, "wb") as file:

            with tqdm(
                total=total_size,
                unit="B",
                unit_scale=True,
                desc=gz_path.name
            ) as progress:

                for chunk in response.iter_content(
                    chunk_size=1024 * 1024
                ):

                    if chunk:
                        file.write(chunk)
                        progress.update(len(chunk))

    return gz_path


def decompress_gzip(gz_path: Path, tif_path: Path):

    if tif_path.exists():
        print(f"Already extracted: {tif_path.name}")
        return

    print(f"Extracting: {tif_path.name}")

    with gzip.open(gz_path, "rb") as source:
        with open(tif_path, "wb") as target:
            shutil.copyfileobj(source, target)

    gz_path.unlink()


def main():

    RAW_CHIRPS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    successful = 0

    for year in range(
        START_YEAR,
        END_YEAR + 1
    ):

        for month in range(1, 13):

            filename = (
                f"chirps-v2.0."
                f"{year}."
                f"{month:02d}.tif"
            )

            gz_filename = filename + ".gz"

            url = (
                CHIRPS_BASE_URL
                + gz_filename
            )

            gz_path = (
                RAW_CHIRPS_DIR
                / gz_filename
            )

            tif_path = (
                RAW_CHIRPS_DIR
                / filename
            )

            try:

                download_file(
                    url,
                    gz_path
                )

                decompress_gzip(
                    gz_path,
                    tif_path
                )

                successful += 1

            except requests.HTTPError as error:

                print()
                print(
                    f"FAILED: {gz_filename}"
                )
                print(error)

            except Exception as error:

                print()
                print(
                    f"FAILED: {gz_filename}"
                )
                print(error)

    print()

    if successful == 12:
        print(
            "CHIRPS download completed successfully."
        )
    else:
        raise SystemExit(
            f"CHIRPS download incomplete: "
            f"{successful}/12 files downloaded."
        )


if __name__ == "__main__":
    main()