import pandas as pd

# 1. Compare fossil and renewable energy over time for a country
def fossil_vs_renewable_energy(df, iso_code):
    df_country = df[df["iso_code"] == iso_code].copy()

    df_country["fossil_energy"] = df_country[["coal_consumption", "oil_consumption", "gas_consumption"]].sum(axis=1)
    df_country["renewables_energy"] = df_country[["solar_consumption", "wind_consumption", "hydro_consumption", "biofuel_consumption"]].sum(axis=1)

    return df_country[["year", "fossil_energy", "renewables_energy"]].dropna().sort_values("year")

# 2. Compute annual growth rates for fossil and renewable energy
def energy_growth_rates(df, iso_code):
    df_country = fossil_vs_renewable_energy(df, iso_code)
    df_country["fossil_growth"] = df_country["fossil_energy"].pct_change() * 100
    df_country["renewable_growth"] = df_country["renewables_energy"].pct_change() * 100
    return df_country.dropna()

def energy_shares(df, iso_code):
    df_country = _prepare_energy_columns(df[df["iso_code"] == iso_code])
    df_country = df_country.dropna(subset=["fossil_energy", "renewables_energy"])
    df_country["total_energy"] = df_country["fossil_energy"] + df_country["renewables_energy"]
    df_country["fossil_share"] = df_country["fossil_energy"] / df_country["total_energy"] * 100
    df_country["renewable_share"] = df_country["renewables_energy"] / df_country["total_energy"] * 100
    return df_country[["year", "fossil_share", "renewable_share"]].sort_values("year")

# 1. Country-level displacement score over time
def displacement_score(df, iso_code):
    df_country = _prepare_energy_columns(df[df["iso_code"] == iso_code])
    df_country = df_country.sort_values("year")
    df_country["fossil_growth"] = df_country["fossil_energy"].pct_change() * 100
    df_country["renewable_growth"] = df_country["renewables_energy"].pct_change() * 100
    df_country["displacement_score"] = df_country["renewable_growth"] - df_country["fossil_growth"]
    return df_country[["year", "displacement_score"]].dropna()


def compare_displacement_scores(df, latest_only=True):
    scores = []
    countries = df["iso_code"].dropna().unique()

    for code in countries:
        growth_df = energy_growth_rates(df, code)
        if growth_df is None or growth_df.empty:
            continue

        # Calculate displacement score: renewable - fossil
        growth_df["displacement_score"] = growth_df["renewable_growth"] - growth_df["fossil_growth"]

        growth_df["country"] = df[df["iso_code"] == code]["country"].iloc[0]

        if latest_only:
            last = growth_df.sort_values("year", ascending=False).head(1)
            scores.append(last[["year", "country", "displacement_score"]])
        else:
            scores.append(growth_df[["year", "country", "displacement_score"]])

    return pd.concat(scores, ignore_index=True)


# Helper to compute fossil and renewable energy columns
def _prepare_energy_columns(df):
    df = df.copy()
    df["fossil_energy"] = df[["coal_consumption", "oil_consumption", "gas_consumption"]].sum(axis=1)
    df["renewables_energy"] = df[["solar_consumption", "wind_consumption", "hydro_consumption", "biofuel_consumption"]].sum(axis=1)
    return df


# 3. Per capita fossil energy vs GDP growth

def fossil_per_capita_vs_gdp(df, iso_code):
    df_country = df[df["iso_code"] == iso_code].sort_values("year")
    df_country = df_country.dropna(subset=["population", "gdp"])
    df_country = _prepare_energy_columns(df_country)
    df_country["fossil_per_capita"] = df_country["fossil_energy"] / df_country["population"]
    df_country["gdp_growth"] = df_country["gdp"].pct_change() * 100
    df_country["fossil_growth"] = df_country["fossil_per_capita"].pct_change() * 100
    return df_country[["year", "gdp_growth", "fossil_growth"]].dropna()