import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
import pandas as pd

from config.settings import PROCESSED_DIR


def calculate_statistics():

    input_file = (
        PROCESSED_DIR
        / "nairobi_rainfall.csv"
    )


    df = pd.read_csv(
        input_file
    )


    # --------------------------------------------------
    # BASIC STATISTICS
    # --------------------------------------------------

    average_monthly = (
        df["rainfall_mm"].mean()
    )


    maximum_monthly = (
        df["rainfall_mm"].max()
    )


    minimum_monthly = (
        df["rainfall_mm"].min()
    )


    # --------------------------------------------------
    # ANNUAL TOTALS
    # --------------------------------------------------

    annual = (
        df
        .groupby("year")["rainfall_mm"]
        .sum()
    )


    average_annual = (
        annual.mean()
    )


    maximum_annual = (
        annual.max()
    )


    minimum_annual = (
        annual.min()
    )


    # --------------------------------------------------
    # MONTHLY CLIMATOLOGY
    # --------------------------------------------------

    monthly = (
        df
        .groupby("month")["rainfall_mm"]
        .mean()
    )


    wettest_month = (
        monthly.idxmax()
    )


    wettest_month_value = (
        monthly.max()
    )


    # --------------------------------------------------
    # OUTPUT
    # --------------------------------------------------

    statistics = {

        "average_monthly_mm":
            average_monthly,

        "maximum_monthly_mm":
            maximum_monthly,

        "minimum_monthly_mm":
            minimum_monthly,

        "average_annual_mm":
            average_annual,

        "maximum_annual_mm":
            maximum_annual,

        "minimum_annual_mm":
            minimum_annual,

        "wettest_month":
            wettest_month,

        "wettest_month_average_mm":
            wettest_month_value,

    }


    output = (
        PROCESSED_DIR
        / "nairobi_rainfall_summary.csv"
    )


    pd.DataFrame(
        [statistics]
    ).to_csv(
        output,
        index=False
    )


    print()
    print(
        "Rainfall statistics:"
    )


    for key, value in statistics.items():

        print(
            f"{key}: {value}"
        )


if __name__ == "__main__":

    calculate_statistics()