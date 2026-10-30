"""
STEP 6: Integrates measurements data with ancillary information, such as coordinates, tree ID, and tree species, by
        matching each measurement to the corresponding device installation and validity period.
"""

from pathlib import Path
import pandas as pd

# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------
SITE_NAME = "viote"
SITE_NAME_AFTER_JOIN = "Viote"

ANCILLARY_DATA_PATH = "../input_data/anc_data.xlsx"

BASE_DIR = Path("../data/output_data_tool")

DATA_PATH = (
    BASE_DIR
    / SITE_NAME
    / f"df_merged_{SITE_NAME}.csv"
)

MISSING_MATCHES_PATH = (
    BASE_DIR
    / SITE_NAME
    / "missing_ancillary_matches.csv"
)

EXPORT_PATH = (
    BASE_DIR
    / SITE_NAME
    / f"df_complete_{SITE_NAME}.csv"
)

# ---------------------------------------------------------------------
# Other constants - do not edit
# ---------------------------------------------------------------------
# Necessary since there are sites with multiple names in the ancillary DataFrame, e.g. "molveno fa" and "molveno ar"
SITE_NAMES_MAP = {
    "cembra": ["cembra"],
    "lavarone": ["lavarone"],
    "molveno": ["molveno fa", "molveno ar"],
    "valcanali": ["val canali fa", "val canali ar"],
    "vallomasona": ["val lomasona"],
    "viote": ["viote ar"],
}

SITE_NAMES = SITE_NAMES_MAP[SITE_NAME]

ANCILLARY_COLUMNS_TO_DROP = [
    "Abbr_SPECIE",
    "Sample_SPECIF",
    "Sample_TYPE",
    "Sample_CATEG",
    "Sample_NOTE",
]

TECHNICAL_COLUMNS_TO_DROP = [
    "_row_id",
    "_serial",
    "_t",
    "_start",
    "_end",
    "Sample_NAME",
    "SA_DATARIL",
    "SA_DATAFIN",
    "device_type",
]

COLUMNS_TO_RENAME = {
    "source_type": "source_string_type",
    "ID": "serial_number",
    "date": "timestamp",
    "Luogo": "site",
    "E_smpl_25832": "E_25832",
    "N_smpl_25832": "N_25832",
    "IDTree": "ID_tree",
    "Specie": "tree_species",
}

EXPORT_COLUMNS = [
    "site",
    "timestamp",
    "serial_number",
    "ID_tree",
    "tree_species",
    "E_25832",
    "N_25832",
    "airT",
    "dT1",
    "dTmax1_filtered",
    "dT2",
    "dTmax2_filtered",
    "SFD1",
    "SFD2",
    "dis",
    "yaw",
    "pitch",
    "roll",
    "VISBL_450",
    "VISBL_500",
    "VISBL_550",
    "VISBL_570",
    "VISBL_600",
    "VISBL_650",
    "NIR_610",
    "NIR_680",
    "NIR_730",
    "NIR_760",
    "NIR_810",
    "NIR_860",
]

# Column mapping
SERIAL_DF1 = "ID"
TIMESTAMP_DF1 = "date"

SERIAL_DF2 = "Sample_NAME"
START_DATE_DF2 = "SA_DATARIL"
END_DATE_DF2 = "SA_DATAFIN"
SITE_DF2 = "Luogo"

def normalize_key(x):
    """
    Normalize serial-number keys.

    Accepts either a single string or a pandas Series / array-like object.
    """
    if isinstance(x, str):
        s = x
        s = s.strip().upper()
        return s

    s = pd.Series(x) if not isinstance(x, pd.Series) else x
    s = s.astype("string").str.strip().str.upper()
    return s


def main() -> None:
    df1 = pd.read_csv(DATA_PATH)
    df2 = pd.read_excel(ANCILLARY_DATA_PATH, dtype=str)

    print(f"Initial shape: {df1.shape}")

    # Technical ID used for subsequent checks
    df1["_row_id"] = range(len(df1))

    # Filter ancillary data by site
    df2 = df2[
        df2[SITE_DF2]
        .astype("string")
        .str.strip()
        .str.casefold()
        .isin(SITE_NAMES)
    ].copy()

    df2 = df2.drop(
        columns=ANCILLARY_COLUMNS_TO_DROP,
        errors="ignore"
    )

    # Prepare serial numbers and timestamps
    df1["_serial"] = normalize_key(df1[SERIAL_DF1])
    df2["_serial"] = normalize_key(df2[SERIAL_DF2])

    # Parsing date
    df1["_t"] = pd.to_datetime(df1[TIMESTAMP_DF1], errors="coerce", utc=True)

    df2["_start"] = pd.to_datetime(df2[START_DATE_DF2], errors="coerce", utc=True)
    df2["_end"] = pd.to_datetime(df2[END_DATE_DF2], errors="coerce", utc=True)

    # Open-ended interval when installation end date is missing
    df2["_end"] = df2["_end"].fillna(pd.Timestamp.max.tz_localize("UTC"))

    df1 = df1.dropna(subset=["_serial", "_t"]).copy()
    df2 = df2.dropna(subset=["_serial", "_start"]).copy()

    df1 = df1.sort_values(["_t", "_serial"], kind="mergesort").reset_index(drop=True)
    df2 = df2.sort_values(["_start", "_serial"], kind="mergesort").reset_index(drop=True)

    # For each df1 row, select the df2 row with the same serial number and the latest installation
    # start date <= measurement timestamp.
    joined = pd.merge_asof(
        df1,
        df2,
        left_on="_t",
        right_on="_start",
        by="_serial",
        direction="backward",
        allow_exact_matches=True,
    )

    # Check that the measurement timestamp actually falls within the installation validity interval.
    out = joined[
        (joined["_t"] >= joined["_start"]) &
        (joined["_t"] < joined["_end"])
    ].copy()

    # Check measurements without ancillary match
    matched_row_ids = set(out["_row_id"])
    missing = df1[~df1["_row_id"].isin(matched_row_ids)].copy()

    if not missing.empty:
        print("Rows df1 without match in ancillary data:", len(missing))
        missing.to_csv(
            MISSING_MATCHES_PATH,
            index=False
        )

    out["Luogo"] = SITE_NAME_AFTER_JOIN

    out = out.drop(columns=TECHNICAL_COLUMNS_TO_DROP, errors="ignore")

    out.rename(columns=COLUMNS_TO_RENAME, inplace=True)

    out_export = out[EXPORT_COLUMNS].copy()

    # Format numeric columns with a maximum of two decimal places
    numeric_columns = out_export.select_dtypes(include="number").columns

    for col in numeric_columns:
        out_export[col] = out_export[col].map(
            lambda x: "" if pd.isna(x) else f"{x:.2f}".rstrip("0").rstrip(".")
        )

    out_export.to_csv(
        EXPORT_PATH,
        index=False
    )

    print(f"Output saved to: {EXPORT_PATH}")
    print(f"Final shape: {out_export.shape}")

if __name__ == "__main__":
    main()
