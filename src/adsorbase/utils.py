import pandas as pd
from pathlib import Path
import os

ROOT_PATH = Path(__file__).resolve().parents[2]
custom_path = ROOT_PATH / 'data/custom.csv'
csv_file = ROOT_PATH / 'data/adsorbents.csv'


column_titles = []

with open(ROOT_PATH/'data/adsorbents.csv', 'r', encoding='utf-8') as database:
    header = database.read().splitlines()[0]
    column_titles = header.split(',')

axis_options = column_titles[2:5]


def load_df(filepath: Path | str = Path(ROOT_PATH / 'data/adsorbents.csv')) -> pd.DataFrame:
    return pd.read_csv(filepath, sep=',')

def current_data() -> pd.DataFrame:
        if os.path.exists(custom_path):
            df = pd.read_csv(custom_path)
        else:
            df = pd.read_csv(csv_file)
        return df


if __name__ == '__main__':
    print(load_df())
    print(axis_options)
