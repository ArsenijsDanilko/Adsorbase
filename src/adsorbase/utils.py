import pandas as pd
from pathlib import Path
import importlib.resources as resources
from numpy import nan

_PACKAGE_DATA = 'adsorbase.data'
_DATABASE_CSV = 'adsorbents.csv'
_CUSTOM_CSV = 'custom.csv'


def load_adsorbents_csv(filename: str) -> pd.DataFrame:
    """Read the default CSV file bundled within the adsorbase.data package."""
    with resources.files(_PACKAGE_DATA).joinpath(filename).open('r', encoding='utf-8') as file:
        return pd.read_csv(file)


def _read_csv_headers(filename: str) -> list[str]:
    """Read only the header of a CSV file."""
    with resources.files(_PACKAGE_DATA).joinpath(filename).open("r", encoding="utf-8") as file:
        return file.readline().strip().split(",")


def _custom_csv_path() -> Path:
    """Use ~/.adsorbase/custom.csv for user-defined data."""

    path = Path.home() / ".adsorbase" / _CUSTOM_CSV
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def load_df() -> pd.DataFrame:
    """Load the default adsorbent database of the package"""
    return load_adsorbents_csv(_DATABASE_CSV)


def current_data() -> pd.DataFrame:
    """Load custom data if it exists, otherwise fallback to default 
    data. Looks for custom.csv next to the script that imports this module."""

    # Look for custom.csv in the same directory as the __main__ script
    local_custom_path = _custom_csv_path()
    if local_custom_path.exists():
        return pd.read_csv(local_custom_path)

    return load_df()


def insert_into_csv(name, ads_type, BET, Pore, Ads, T, P) -> None:
    """Insert a new adsorbent row into custom.csv"""
    num_data = [BET, Pore, Ads, T, P]

    num_data = [nan if x is None else x for x in num_data]

    new_data = pd.DataFrame(
        [[name, ads_type] + num_data],
        columns=column_titles
    )
    updated = pd.concat([current_data(), new_data], ignore_index=True)

    custom_path = _custom_csv_path()
    custom_path.parent.mkdir(parents=True, exist_ok=True)
    updated.to_csv(custom_path, index=False)


column_titles = _read_csv_headers(_DATABASE_CSV)
axis_options = column_titles[2:5]

if __name__ == '__main__':
    print(load_df())
    print(axis_options)
