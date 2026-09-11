from pathlib import Path


# ============================================================
# PROJECT
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"


# ============================================================
# RAW DATA
# ============================================================

RAW_DIR = DATA_DIR / "raw"

RAW_CHIRPS_DIR = RAW_DIR / "rainfall"

FLOOD_RAW_DIR = RAW_DIR / "flood"

COP_DEM_DIR = RAW_DIR / "cop_dem"


# ============================================================
# PROCESSED DATA
# ============================================================

PROCESSED_DIR = DATA_DIR / "processed" / "rainfall"


# ============================================================
# CHIRPS
# ============================================================

CHIRPS_BASE_URL = (
    "https://data.chc.ucsb.edu/products/CHIRPS-2.0/"
    "global_monthly/tifs/"
)
START_YEAR = 2025

END_YEAR = 2025


# ============================================================
# PROPERTY
# ============================================================

NAIROBI_LAT = -1.2921

NAIROBI_LON = 36.8219