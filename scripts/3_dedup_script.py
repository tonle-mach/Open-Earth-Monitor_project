"""
STEP 3: Removes duplicate measurements when multiple TT Clouds serve the same site, ensuring that measurements
        from the same device are not ingested multiple times through different TT Clouds.

        After setting the site name, the reference TT Cloud ID, and the TT Cloud to be deduplicated,
        update the file name at each run, according to the DataFrames to be processed.
"""
import pandas as pd

# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------
SITE_NAME = "valcanali"
CLOUD_ID_REF = "C1990068"
CLOUD_ID_TO_DEDUP = "C1990069"
FILE_NAME = "df4B"

def remove_rows_already_present(
    df_reference: pd.DataFrame,
    df_to_clean: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Remove from df_to_clean rows already present in df_reference.
    All columns are used as the comparison key.

    Returns
    -------
    duplicated_rows : pd.DataFrame
        Rows present in both DFs.

    cleaned_df : pd.DataFrame
        Rows from df_to_clean not present in df_reference.
    """
    if set(df_reference.columns) != set(df_to_clean.columns):
        raise ValueError("The two DataFrames don't have the same columns.")

    df_to_clean = df_to_clean[df_reference.columns].copy()
    key_cols = list(df_reference.columns)

    merged = df_to_clean.merge(
        df_reference.drop_duplicates(),
        on=key_cols,
        how="left",
        indicator=True,
    )

    duplicated_mask = merged["_merge"] == "both"

    duplicated_rows = df_to_clean.loc[duplicated_mask.values].copy()
    cleaned_df = df_to_clean.loc[~duplicated_mask.values].copy()

    return duplicated_rows, cleaned_df

def main() -> None:
    path_df_1 = f"../data/output_data_tool/{SITE_NAME}/{CLOUD_ID_REF}/{FILE_NAME}.csv"
    path_df_2 = f"../data/output_data_tool/{SITE_NAME}/{CLOUD_ID_TO_DEDUP}/{FILE_NAME}.csv"
    path_df_out = f"../data/output_data_tool/{SITE_NAME}/{CLOUD_ID_TO_DEDUP}/{FILE_NAME}_cleaned.csv"

    df_1 = pd.read_csv(path_df_1)
    df_2 = pd.read_csv(path_df_2)

    duplicates, df_new_cleaned = remove_rows_already_present(
        df_reference=df_1,
        df_to_clean=df_2,
    )

    print(f"Duplicated rows removed: {len(duplicates)}")
    print(f"Rows kept after deduplication: {len(df_new_cleaned)}")

    df_new_cleaned.to_csv(path_df_out, index=False)

if __name__ == "__main__":
    main()
