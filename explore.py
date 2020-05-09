"""
Scratch code for exploring the data set.
"""
from datetime import datetime
import json
import os
from pathlib import Path


from dotenv import load_dotenv
import pandas as pd  # TODO - REPLACE WITH THE MODIN MODULE (FOR MULTI-CORE PANDAS)
import pytz

load_dotenv(dotenv_path='.env_file')


def get_csv_list(dir_path):
    """"Get list of .CSV files in the supplied directory path"""
    csv_list = [Path(dir_path) / f for f in os.listdir(dir_path) if f.endswith('.csv')]
    return sorted(csv_list)


def parse_dt(inp_str):
    """Parse datetime string format found in CSV files and append time-zone information"""
    return pytz.timezone('US/Mountain').localize(datetime.strptime(inp_str, '%Y%m%d-%H%M%S'))


def build_df(dir_path):
    """Build concatenated and properly indexed DataFrame from CSV files"""
    df_list = []
    # Load data types from JSON
    with open(Path(os.getenv("LABELS_JSON"))) as dtypes_file:
        dtypes = json.load(dtypes_file)

    # Limit columns to only the "process variable" data (PV), excluding set-points and outputs
    cols = [k for k in dtypes.keys() if k.endswith('PV.CV')]
    cols.append('Unnamed: 0')

    # Parse all CSVs and concatenate into single DataFrame
    for csv_path in get_csv_list(dir_path):
        df_list.append(pd.read_csv(csv_path, dtype=dtypes, converters={'time': parse_dt}, usecols=cols))
    df = pd.concat(df_list)

    # Create combined sequential index for the concatenated DF:
    # TODO - CONSIDER DROPPING NUMERIC INDEX AND USING DATETIME COLUMN INSTEAD
    df.iloc[:, 0] = list(range(0, df.shape[0]))
    df.set_index('Unnamed: 0', drop=True, inplace=True)

    df.fillna(method='ffill', inplace=True)
    return df


if __name__ == "__main__":
    data_frame = build_df(dir_path=os.getenv("CSV_PATH"))
    print(data_frame)
