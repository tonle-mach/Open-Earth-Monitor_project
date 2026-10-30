"""
STEP 4: Harmonizes and combines the different DataFrames previously generated for a specific TT Cloud into a single
        DataFrame with a common structure. This process has to be performed for each TT Cloud ID.
"""

from pathlib import Path
import pandas as pd
import numpy as np

# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------
SITE_NAME = "viote"
CLOUD_ID = "C1970066"
USE_CLEANED_FILES = False # True: if the script runs in the folder with "_cleaned.csv" files. False: otherwise
BASE_DIR = Path("../data/output_data_tool")

# ---------------------------------------------------------------------
# Other constants - do not edit
# ---------------------------------------------------------------------
CLEANED_SUFFIX = "_cleaned" if USE_CLEANED_FILES else ""
COMMON_COLUMNS = [
        "source_type",
        "ID",
        "device_type",
        "date",
        "Vbat",
        "DOY",
        "month",
        "year",
        "airT",
        "RH",
        "Tref_start",
        "Tref_end",
        "Theat_start",
        "Theat_end",
        "dT_heat",
        "dTon",
        "dToff",
        "dT1",
        "dTmax1",
        "dTmax1_filtered",
        "dT2",
        "dTmax2",
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
        "ndvi",
    ]

INPUT_FILES = {
    "4D": "df4D",
    "45": "df45",
    "49": "df49",
    "4B": "df4B",
}

def load_dataframe(path: Path) -> pd.DataFrame | None:
    """
    Load a CSV file if available.

    Parameters
    ----------
    path : Path
        Path to the CSV file.

    Returns
    -------
    pd.DataFrame | None
        Loaded DataFrame, or None if the file does not exist.
    """
    if not path.exists():
        print(f"File not found, skipping: {path}")
        return None

    df = pd.read_csv(path)
    print(f"Loaded {path.name}: {df.shape}")

    return df


def harmonize_dataframes(dataframes: dict[str, pd.DataFrame | None],) -> pd.DataFrame:
    """
    Harmonize DataFrames to a common schema and concatenate them.

    Missing columns are added as NaN. Each DataFrame is labelled with
    its corresponding source type before concatenation.

    Parameters
    ----------
    dataframes : dict[str, pd.DataFrame | None]
        Mapping between source type and DataFrame.

    Returns
    -------
    pd.DataFrame
        Harmonized and concatenated DataFrame.
    """
    harmonized_dfs = []

    for source_type, df in dataframes.items():

        if df is None or df.empty:
            print(
                f"Skipping source type {source_type}: "
                "DataFrame missing or empty."
            )
            continue

        print(f"\nSource type: {source_type}")
        print(f"Shape before harmonization: {df.shape}")

        df = df.copy()
        df["source_type"] = source_type

        for column in COMMON_COLUMNS:
            if column not in df.columns:
                df[column] = np.nan

        df = df[COMMON_COLUMNS]

        print(f"Shape after harmonization: {df.shape}")

        harmonized_dfs.append(df)

    if not harmonized_dfs:
        print("No DataFrames available.")
        return pd.DataFrame(columns=COMMON_COLUMNS)

    return pd.concat(harmonized_dfs, ignore_index=True)



def main() -> None:
    input_dir = BASE_DIR / SITE_NAME / CLOUD_ID

    dataframes = {
        source_type: load_dataframe(
            input_dir / f"{filename}{CLEANED_SUFFIX}.csv"
        )
        for source_type, filename in INPUT_FILES.items()
    }

    input_shapes = {
        source_type: None if df is None else df.shape
        for source_type, df in dataframes.items()
    }

    print("\nInput shapes:")
    for source_type, shape in input_shapes.items():
        print(f"  {source_type}: {shape}")

    expected_rows = sum(
        len(df)
        for df in dataframes.values()
        if df is not None
    )

    print(f"\nExpected rows before harmonization: {expected_rows}")

    df_all = harmonize_dataframes(dataframes)

    output_path = input_dir / f"df_all_{CLOUD_ID}.csv"
    df_all.to_csv(output_path, index=False)

    print(f"\nOutput written to: {output_path}")
    print(f"Final shape: {df_all.shape}")

    if not df_all.empty:
        print("\nSource type counts:")
        print(df_all["source_type"].value_counts())


if __name__ == "__main__":
    main()