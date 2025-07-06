# scripts/Electricity_Insights.py

from django.conf import settings
import pandas as pd
import os

DATA_PATH = os.path.join(settings.BASE_DIR, 'data')

def load_power_plant_data(filename="global_power_plant_database.csv"):
    filepath = os.path.join(DATA_PATH, filename)
    df = pd.read_csv(filepath, encoding='utf-8')
    return df

def get_country_plant_data(df, country_code):
    return df[df['country'] == country_code]

def get_total_capacity(df_country):
    return df_country['capacity_mw'].sum()

def get_fuel_mix_distribution(df_country):
    value_counts = df_country['primary_fuel'].value_counts(normalize=True)
    df = value_counts.reset_index()
    df.columns = ['Fuel_Type', 'proportion']
    return df

def get_fuel_capacity_distribution(df_country):
    return df_country.groupby('primary_fuel')['capacity_mw'].sum().reset_index().sort_values(by='capacity_mw', ascending=False)

def get_location_map_df(df_country):
    return df_country[['name', 'latitude', 'longitude', 'primary_fuel', 'capacity_mw']]

def capacity_over_time(df_country):
    df_valid = df_country.dropna(subset=["commissioning_year"])
    return (
        df_valid.groupby("commissioning_year")["capacity_mw"]
        .sum()
        .reset_index()
        .sort_values(by="commissioning_year")
    )

def average_capacity_by_fuel(df_country):
    return (
        df_country.groupby("primary_fuel")["capacity_mw"]
        .mean()
        .reset_index()
        .rename(columns={"capacity_mw": "avg_capacity_mw"})
        .sort_values(by="avg_capacity_mw", ascending=False)
    )

def fuel_mix_over_time(df_country):
    df_valid = df_country.dropna(subset=["commissioning_year"])
    return (
        df_valid.groupby(["commissioning_year", "primary_fuel"])["capacity_mw"]
        .sum()
        .reset_index()
    )

def generation_efficiency(df_country, year=2017):
    est_col = f"estimated_generation_gwh_{year}"
    act_col = f"generation_gwh_{year}"

    df = df_country.dropna(subset=[act_col, est_col])
    df["utilization_ratio"] = df[act_col] / df[est_col]
    return df[["name", "primary_fuel", act_col, est_col, "utilization_ratio"]].sort_values(by="utilization_ratio", ascending=False)

