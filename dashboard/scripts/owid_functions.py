import pandas as pd
from django.conf import settings
import os

DATA_PATH = os.path.join(settings.BASE_DIR, 'data')

def load_owid_data():
    filepath = os.path.join(DATA_PATH, "owid-energy-data.csv")
    return pd.read_csv(filepath)

# 1. Renewable share over time (Q1 + Q2)
def renewable_share_over_time(df, country_code):
    subset = df[df["iso_code"] == country_code]
    return subset[["year", "renewables_share_energy"]].dropna()

# 2. Renewable source breakdown (Q3)
def renewable_source_breakdown(df, country_code, year):
    subset = df[(df["iso_code"] == country_code) & (df["year"] == year)]
    if subset.empty:
        return None

    solar = subset["solar_share_elec"].values[0] or 0
    wind = subset["wind_share_elec"].values[0] or 0
    hydro = subset["hydro_share_elec"].values[0] or 0
    total_renewable = subset["renewables_share_energy"].values[0] or 0

    other = total_renewable - (solar + wind + hydro)

    values = {
        "Solar": round(solar, 2),
        "Wind": round(wind, 2),
        "Hydro": round(hydro, 2),
        "Other": round(other, 2) if other > 0 else 0
    }

    return {k: v for k, v in values.items() if v > 0}

# 3. Top countries by renewable share (Q4)
def top_countries_by_renewable(df, year, top_n=10):
    subset = df[df["year"] == year]
    return subset[["country", "iso_code", "renewables_share_energy"]].dropna().sort_values(
        by="renewables_share_energy", ascending=False
    ).head(top_n)

# 4. Fastest growing renewable share (Q5)
def fastest_growth_in_renewables(df, start_year, end_year, top_n=10):
    subset = df[df["year"].isin([start_year, end_year])]
    
    # Aggregate to ensure unique iso_code-year pairs
    grouped = (
        subset.groupby(["iso_code", "year"])["renewables_share_energy"]
        .mean()
        .reset_index()
    )
    
    pivot = grouped.pivot(index="iso_code", columns="year", values="renewables_share_energy").dropna()

    pivot["growth_pct"] = ((pivot[end_year] - pivot[start_year]) / pivot[start_year]) * 100
    return pivot.sort_values("growth_pct", ascending=False).head(top_n).reset_index()


# 5. Electricity mix of a country (Q6 + Q7)
def electricity_mix(df, country_code, year):
    subset = df[(df["iso_code"] == country_code) & (df["year"] == year)]
    if subset.empty:
        return None

    row = subset.iloc[0]
    return {
        "Fossil": row["fossil_electricity"] or 0,
        "Renewable": row["low_carbon_electricity"] or 0
    }
