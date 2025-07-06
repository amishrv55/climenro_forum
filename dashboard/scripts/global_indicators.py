from django.conf import settings
import os
import pandas as pd
from scipy.stats import linregress
import xarray as xr

# --- Base Directories ---
DATA_PATH = os.path.join(settings.BASE_DIR, 'data')

# --- Loaders ---
def load_zonal_temperature_data(filename="Zonal_annual_means.csv"):
    filepath = os.path.join(DATA_PATH, filename)
    df = pd.read_csv(filepath)
    df.columns = df.columns.str.strip()

    if 'Year' not in df.columns:
        df.columns = df.iloc[0]
        df = df[1:]
        df.reset_index(drop=True, inplace=True)

    df['Year'] = df['Year'].astype(int)
    return df


def load_global_temperature_data(filename="Global_annual_means.csv"):
    filepath = os.path.join(DATA_PATH, filename)
    df = pd.read_csv(filepath, skiprows=1)
    df.columns = df.columns.str.strip()

    if 'Year' not in df.columns:
        df.columns = df.iloc[0]
        df = df[1:]
        df.reset_index(drop=True, inplace=True)

    df['Year'] = df['Year'].astype(int)
    return df

# --- Temperature Trends ---
def get_global_annual_trend(df):
    return df[['Year', 'J-D']].rename(columns={'J-D': 'Annual'}).dropna()


def get_zonal_trend_summary(df):
    latest_decade = df[df['Year'] >= df['Year'].max() - 10]
    zones = [col for col in df.columns if col != 'Year']
    summary = latest_decade[zones].mean().reset_index()
    summary.columns = ['Zone', 'Avg_Warming']
    return summary.sort_values("Avg_Warming", ascending=False).reset_index(drop=True)

ZONE_NAMES = {
    "64N-90N": "Arctic",
    "44N-64N": "Northern Temperate",
    "24N-44N": "Mid-Latitudes North",
    "24S-24N": "Tropics (Equator)",
    "44S-24S": "Mid-Latitudes South",
    "64S-44S": "Southern Temperate",
    "90S-64S": "Antarctica",
    "Glob": "Global Avg",
    "NHem": "Northern Hemisphere",
    "SHem": "Southern Hemisphere"
}

def get_warming_rate_by_zone(df, zones):
    results = []
    for zone in zones:
        x = df['Year']
        y = df[zone]
        slope, _, _, p_value, _ = linregress(x, y)
        results.append({
            "zone_code": zone,
            "zone_name": ZONE_NAMES.get(zone, zone),
            "rate_per_decade": slope * 10,
            "p_value": p_value
        })
    return pd.DataFrame(results)

def get_temperature_rate_of_change(df, zone="Glob"):
    x = df['Year']
    y = df[zone]
    slope, _, _, p_value, _ = linregress(x, y)
    return slope * 10, p_value  # °C per decade

# --- Sea Level ---
def load_sea_level_data(file="GRACE_GOMA.nc"):
    filepath = os.path.join(DATA_PATH, file)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Sea level data file not found: {filepath}")

    ds = xr.open_dataset(filepath)
    for var in ds.data_vars:
        if 'time' in ds[var].dims:
            df = ds[[var]].to_dataframe().reset_index()
            df = df.rename(columns={var: "sea_level_anomaly"})
            df.dropna(subset=["sea_level_anomaly"], inplace=True)
            return df

    raise ValueError("No valid sea level anomaly variable found in dataset.")

def summarize_sea_level_trend(df):
    df = df.sort_values("time")
    df["year"] = df["time"].dt.year + df["time"].dt.dayofyear / 365.0

    x = df["year"]
    y = df["sea_level_anomaly"]

    slope, intercept, r_value, p_value, std_err = linregress(x, y)

    return {
        "start_year": int(x.min()),
        "end_year": int(x.max()),
        "rate_mm_per_year": slope,
        "total_rise_mm": (x.max() - x.min()) * slope,
        "p_value": p_value,
        "r_squared": r_value ** 2
    }

def get_sea_level_trend_line(df):
    df = df.copy()
    df["year"] = df["time"].dt.year + df["time"].dt.dayofyear / 365.0
    return df[["time", "sea_level_anomaly"]]

# --- Gas Concentration ---
def load_gas_data(gas_file, base_path=DATA_PATH):
    filepath = os.path.join(base_path, gas_file)
    df = pd.read_csv(filepath)
    df = df.dropna(subset=["average"])
    df["datetime"] = pd.to_datetime(df[["year", "month"]].assign(day=15))
    return df

# --- CLI Test ---
if __name__ == "__main__":
    zonal_df = load_zonal_temperature_data()
    global_df = load_global_temperature_data()

    print(get_global_annual_trend(global_df).tail())
    print(get_zonal_trend_summary(zonal_df))
    print(get_temperature_rate_of_change(zonal_df, zone="64N-90N"))
