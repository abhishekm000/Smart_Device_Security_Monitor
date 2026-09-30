# Dataset Strategy

This project uses the CICIoT2023 dataset by default. 
Because the full dataset is extremely large (multiple gigabytes), we provide a lightweight Python script to generate a perfectly structural-matching synthetic sample for local testing and development.

## Using Real Data
1. Download CICIoT2023 CSV files.
2. Place them in `data/raw/`.
3. Update the `data_path` parameter in `ml/preprocessing.py` to point to the raw file.

## Features
The dataset contains 46 continuous/discrete features derived from network packet captures, including metrics like Flow Duration, Header Length, Protocol, Packet Rates, TCP flags, and various statistical moments (Mean, Variance, Covariance) of packet lengths and times.
