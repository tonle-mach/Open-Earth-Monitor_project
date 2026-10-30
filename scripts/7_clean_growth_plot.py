"""
STEP 7: Cleans time series showing anomalous stem-growth measurements by setting the affected variable values to NaN.
        Problematic time series (i.e. serials into SERIALS_TO_CLEAN_MAP) are identified through visual inspection.
"""

from pathlib import Path
import pandas as pd
import numpy as np
import os

# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------
SITE_NAME = "molveno"

# ---------------------------------------------------------------------
# Other constants - do not edit
# ---------------------------------------------------------------------
SERIALS_TO_CLEAN_MAP = {
    "cembra": [
        "21990679",
        "21990706",
        "52020088",
        "218C0310",
        "218C0307",
        "52020081",
        "21990705",
        "52020080",
        "52020086",
        "218C0312",
        "218C0301",
        "52020079",
        "218C0305",
        "21980636",
        "52020074",
        "21980634",
        "218C0319",
        "21980605",
        "21990681",
        "218C0315",
        "21980611",
        "218C0314"
    ],
    "lavarone": [
        "22010005",
        "52110084",
        "52010001",
        "52020087",
        "52020061",
        "52020078",
        "52020073",
        "52020067"
    ],
    "molveno": [
        "21990729",
        "21990712",
        "21990718",
        "21990728",
        "21990713",
        "21990736",
        "21990742",
        "21990717",
        "21990725",
        "21980597",
        "21990711",
        "21990747",
        "21980606",
        "21990753",
        "21990751",
        "21990758",
        "21990714",
        "21980625",
        "21990738",
        "21980637",
        "21990730",
        "21990750",
        "21990724",
        "21990734",
        "21990756",
        "21990755",
        "21980608",
        "21980600",
        "21980639",
        "21990683",
        "21990752",
        "21990748",
        "21990757",
        "22010001",
        "52020071",
        "21990743",
        "21990741",
        "21990740",
        "21990733",
        "21990715",
        "21990722"
    ],
    "valcanali": [
        "21990670",
        "21980611",
        "21990692",
        "21990661",
        "21990667",
        "21990702",
        "21990677",
        "21980618",
        "21990684",
        "21990701",
        "21990690",
        "21980622",
        "21990700",
        "21990663",
        "21990698",
        "21990665",
        "21990689",
        "21990707",
        "21990675",
        "21990687",
        "21990659",
        "21990699",
        "21990697",
        "21990669",
        "21990672",
        "21990666",
        "21990695",
        "21990671",
        "21990731",
        "21990693",
        "21990703",
        "21990685",
        "21990732",
        "21990627",
        "21980638",
        "21980629",
        "21980599",
        "21990662",
        "21980610",
        "21990668"
    ],
    "vallomasona": [
        "21980596",
        "21980597",
        "21980599",
        "21980602",
        "21980603",
        "21980606",
        "21980609",
        "21980612",
        "21980613",
        "21980615",
        "21980616",
        "21980617",
        "21980618",
        "21980622",
        "21980623",
        "21980626",
        "21980627",
        "21980630",
        "21980634",
        "21980637"
    ],
    "viote": [
        "21980611",
        "21980614",
        "21980618",
        "21980619",
        "21980622",
        "21980625",
        "21980627",
        "21980630"
    ]
}

SERIALS_TO_CLEAN = SERIALS_TO_CLEAN_MAP[SITE_NAME]

BASE_DIR = Path("../data/output_data_tool")

DATA_PATH = (
    BASE_DIR
    / SITE_NAME
    / f"df_complete_{SITE_NAME}.csv"
)

EXPORT_PATH = (
    BASE_DIR
    / SITE_NAME
    / f"df_{SITE_NAME}.csv"
)

COMPRESSED_EXPORT_PATH = (
    BASE_DIR
    / SITE_NAME
    / f"df_{SITE_NAME}_compressed.csv.gz"
)




def main() -> None:
    print("Input file size:", os.path.getsize(
        DATA_PATH
    ) / 1024**2, "MB")

    df = pd.read_csv(DATA_PATH)

    mask = df["serial_number"].isin(SERIALS_TO_CLEAN)

    print("Selected rows:", mask.sum())
    print("NaN values before time series cleaning (adding new NaN values):", df["dis"].isna().sum())

    print(
        "'dis' values actually removed:",
        df.loc[mask, "dis"].notna().sum()
    )

    df.loc[mask, "dis"] = np.nan

    print("NaN values after time series cleaning:", df["dis"].isna().sum())

    df.to_csv(
        EXPORT_PATH,
        index=False
    )

    df.to_csv(
        COMPRESSED_EXPORT_PATH,
        index=False,
        compression="gzip"
    )

    print("Output file size:", os.path.getsize(EXPORT_PATH) / 1024**2, "MB")

if __name__ == "__main__":
    main()