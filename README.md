# Open-Earth-Monitor Data Processing Pipeline 
### Task 4.7: Preparation of in-situ data obtained from automated ground observation networks

## Overview

This repository contains a Python-based data processing pipeline developed to clean, harmonize, and integrate in-situ 
datasets collected from multiple IoT devices across different monitoring sites.

The scripts corresponding to step 1 and 2 are derived from the original repository from which this project was forked.

The pipeline processes raw measurement data, removes duplicate observations, consolidates measurements across devices, 
and integrates ancillary information to produce consistent datasets suitable for subsequent analysis.

The workflow consists of seven sequential processing steps.

## Pipeline Description

### 1. Manual Data Pre-processing
**Script:** `1_clean_manual_files.py`

Pre-processes manually downloaded measurement files, when available, preparing them for the subsequent processing steps.

### 2. Initial Data Processing
**Script:** `2_TT_plus_DT_packed_v6_1.py`

Modified version of the original Nature 4.0 data processing tool.

Creates the basic pandas DataFrames containing the measurements required for the subsequent processing steps.

### 3. Duplicate Removal
**Script:** `3_dedup_script.py`

Identifies and removes duplicate measurements that may occur when multiple TT Clouds are deployed at the same monitoring site.

This prevents measurements from the same device from being recorded multiple times through different TT Clouds.

### 4. Data Harmonization per TT Cloud
**Script:** `4_harmonize_df_per_cloud.py`

Combines the different DataFrames generated during step 2 and associated with the same TT Cloud.

### 5. Data Harmonization per Monitoring Site
**Script:** `5_harmonize_df_per_site.py`

Consolidates the DataFrames associated with different TT Clouds operating at the same monitoring site.

This step is particularly relevant when multiple TT Clouds are deployed at a single site.

### 6. Integration of Ancillary Data
**Script:** `6_join_ancillary_data.py`

Enriches the processed measurements by integrating ancillary information, including:

- Geographic coordinates.
- Tree species.

### 7. Stem Growth Data Cleaning
**Script:** `7_clean_growth_plot.py`

Cleans time series containing anomalous stem-growth measurements.

Problematic time series are identified through visual inspection. Values associated with anomalous measurements are subsequently replaced with `NaN`, preserving the remaining measurements.


## Acknowledgments

This repository is based on [TTPlus_datatool repository](https://github.com/valerioCoppola/TTPlus_datatool).

The original data processing tools provided the foundation for this project. Some of the original scripts have been adapted, while additional processing scripts have been developed to extend the workflow with data cleaning, deduplication, harmonization, and ancillary data integration functionalities.

The original authors' contributions are gratefully acknowledged.

## License

The use and distribution of the original components are subject to the terms of their respective license.