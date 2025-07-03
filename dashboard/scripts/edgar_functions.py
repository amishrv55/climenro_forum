import pandas as pd

# 1. Top 5 emitting sectors in a country
def top_sectors_by_country_year(df, country_code, year, top_n=5):
    subset = df[(df['Country_code_A3'] == country_code) & (df['year'] == year)]
    return (
        subset.groupby('ipcc_code_2006_for_standard_report_name')['emissions_mtco2e']
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index()
    )

# 2. Top 5 emitting countries globally
def top_emitting_countries(df, year, top_n=5):
    subset = df[df['year'] == year]
    return (
        subset.groupby('Country_code_A3')['emissions_mtco2e']
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index()
    )

# 3. % of global emissions from top 5 countries
def percent_from_top_emitters(df, year, top_n=5):
    total_global = df[df['year'] == year]['emissions_mtco2e'].sum()
    top_emitters = top_emitting_countries(df, year, top_n)
    top_total = top_emitters['emissions_mtco2e'].sum()
    return round((top_total / total_global) * 100, 2)

# 4. Rank of a country by emissions
def emission_rank(df, country_code, year):
    subset = df[df['year'] == year]
    country_totals = subset.groupby('Country_code_A3')['emissions_mtco2e'].sum().sort_values(ascending=False)
    rank = country_totals.reset_index().reset_index()
    rank.columns = ['rank', 'Country_code_A3', 'emissions_mtco2e']
    result = rank[rank['Country_code_A3'] == country_code]
    return result.iloc[0]['rank'] + 1 if not result.empty else None

# 5. Country vs Top 5 comparison
def country_vs_top5(df, country_code, year):
    top_emitters = top_emitting_countries(df, year, top_n=5)
    
    # Create a DataFrame for the selected country's emission
    country_emission = df[(df['Country_code_A3'] == country_code) & (df['year'] == year)]['emissions_mtco2e'].sum()
    country_row = pd.DataFrame({
        'Country_code_A3': [country_code],
        'emissions_mtco2e': [country_emission]
    })
    
    # Use pd.concat instead of append
    comparison_df = pd.concat([top_emitters, country_row], ignore_index=True)
    
    return comparison_df.sort_values(by='emissions_mtco2e', ascending=False).reset_index(drop=True)


# 6. Emission trend over time for a country
def emission_trend(df, country_code):
    subset = df[df["Country_code_A3"] == country_code]
    return subset.groupby("year")["emissions_mtco2e"].sum().reset_index()

# 7. Fossil vs Bio comparison in a country
def fossil_bio_comparison(df, country_code, year):
    subset = df[(df["Country_code_A3"] == country_code) & (df["year"] == year)]
    return (
        subset.groupby("fossil_bio")["emissions_mtco2e"]
        .sum()
        .reset_index()
        .rename(columns={"fossil_bio": "Source"})
    )

# 8. Top 5 sectors globally (all fuels)
def top_sectors_globally(df, year, top_n=5):
    subset = df[df["year"] == year]
    return (
        subset.groupby("ipcc_code_2006_for_standard_report_name")["emissions_mtco2e"]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index()
    )

# 9. Top 5 fossil-fuel sectors globally
def top_fossil_sectors_globally(df, year, top_n=5):
    subset = df[(df["year"] == year) & (df["fossil_bio"] == "fossil")]
    return (
        subset.groupby("ipcc_code_2006_for_standard_report_name")["emissions_mtco2e"]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index()
    )

# 10. % of emissions from agriculture sectors in a country
def agri_emissions_share(df, country_code, year):
    subset = df[(df["Country_code_A3"] == country_code) & (df["year"] == year)]
    total = subset["emissions_mtco2e"].sum()

    agri_keywords = ["agriculture", "enteric", "manure", "rice", "agricultural soils"]
    agri_subset = subset[subset["ipcc_code_2006_for_standard_report_name"].str.lower().str.contains("|".join(agri_keywords))]
    agri_total = agri_subset["emissions_mtco2e"].sum()

    share = (agri_total / total) * 100 if total > 0 else 0
    return round(share, 2)


# Top CH4 or N2O emitting countries
def top_emitters_by_gas(df, gas, year, top_n=10):
    subset = df[(df["year"] == year) & (df["Substance"].str.upper() == gas.upper())]
    top_emitters = (
        subset.groupby("Country_code_A3")["emissions_mtco2e"]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index()
    )
    return top_emitters

def compare_emission_trends(df, countries):
    subset = df[df["Country_code_A3"].isin(countries)]
    grouped = subset.groupby(["year", "Country_code_A3"])["emissions_mtco2e"].sum().reset_index()
    return grouped.pivot(index="year", columns="Country_code_A3", values="emissions_mtco2e")


def compare_sector_by_country(df, sector_name, year):
    subset = df[(df["year"] == year) & 
                (df["ipcc_code_2006_for_standard_report_name"] == sector_name)]
    return (
        subset.groupby("Country_code_A3")["emissions_mtco2e"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )


def sector_profiles(df, countries, year):
    subset = df[(df["year"] == year) & (df["Country_code_A3"].isin(countries))]
    grouped = subset.groupby(["Country_code_A3", "ipcc_code_2006_for_standard_report_name"])["emissions_mtco2e"].sum().reset_index()
    return grouped.pivot(index="ipcc_code_2006_for_standard_report_name", columns="Country_code_A3", values="emissions_mtco2e").fillna(0)

def stacked_sector_breakdown(df, countries, year):
    subset = df[(df["year"] == year) & (df["Country_code_A3"].isin(countries))]
    return (
        subset.groupby(["Country_code_A3", "ipcc_code_2006_for_standard_report_name"])["emissions_mtco2e"]
        .sum()
        .reset_index()
        .pivot(index="Country_code_A3", columns="ipcc_code_2006_for_standard_report_name", values="emissions_mtco2e")
        .fillna(0)
    )


def sector_contribution(df, country_code, year):
    subset = df[(df["Country_code_A3"] == country_code) & (df["year"] == year)]
    total = subset["emissions_mtco2e"].sum()

    sector_df = (
        subset.groupby("ipcc_code_2006_for_standard_report_name")["emissions_mtco2e"]
        .sum()
        .reset_index()
        .sort_values(by="emissions_mtco2e", ascending=False)
    )

    sector_df["percentage"] = round((sector_df["emissions_mtco2e"] / total) * 100, 2)
    return sector_df


def fastest_growing_sectors(df, start_year=2000, end_year=2023, top_n=5):
    subset = df[(df["year"].isin([start_year, end_year]))]
    grouped = subset.groupby(["ipcc_code_2006_for_standard_report_name", "year"])["emissions_mtco2e"].sum().reset_index()

    pivoted = grouped.pivot(index="ipcc_code_2006_for_standard_report_name", columns="year", values="emissions_mtco2e")
    pivoted["growth_rate_%"] = ((pivoted[end_year] - pivoted[start_year]) / pivoted[start_year]) * 100
    pivoted = pivoted.dropna().sort_values(by="growth_rate_%", ascending=False)
    return pivoted.reset_index().head(top_n)


def manufacturing_vs_global_avg(df, country_code, year):
    sector_name = "Manufacturing Industries and Construction"
    global_mean = (
        df[(df["ipcc_code_2006_for_standard_report_name"] == sector_name) & (df["year"] == year)]
        .groupby("Country_code_A3")["emissions_mtco2e"]
        .sum()
        .mean()
    )

    country_value = df[
        (df["Country_code_A3"] == country_code) &
        (df["year"] == year) &
        (df["ipcc_code_2006_for_standard_report_name"] == sector_name)
    ]["emissions_mtco2e"].sum()

    return round(country_value, 2), round(global_mean, 2)


def cumulative_emissions(df, country_code, start_year=1970, end_year=2023):
    subset = df[
        (df["Country_code_A3"] == country_code) &
        (df["year"] >= start_year) &
        (df["year"] <= end_year)
    ]
    return round(subset["emissions_mtco2e"].sum(), 2)

def cumulative_emissions_n_years(df, country_code, selected_year, n_years):
    start_year = selected_year - n_years + 1
    subset = df[
        (df["Country_code_A3"] == country_code) &
        (df["year"] >= start_year) &
        (df["year"] <= selected_year)
    ]
    return round(subset["emissions_mtco2e"].sum(), 2)

def top_growth_countries(df, end_year, n_years=5, top_n=10):
    start_year = end_year - n_years + 1
    df_start = df[df["year"] == start_year].groupby("Country_code_A3")["emissions_mtco2e"].sum()
    df_end = df[df["year"] == end_year].groupby("Country_code_A3")["emissions_mtco2e"].sum()
    
    df_growth = pd.DataFrame({
        "start_emissions": df_start,
        "end_emissions": df_end
    }).dropna()
    
    df_growth["growth_rate"] = ((df_growth["end_emissions"] - df_growth["start_emissions"]) / df_growth["start_emissions"]) * 100
    df_growth = df_growth[df_growth["start_emissions"] > 0]
    
    return df_growth.sort_values("growth_rate", ascending=False).head(top_n).reset_index()

def compare_country_with_global(df, country_code, year):
    global_df = df[df["year"] == year]
    global_avg = global_df.groupby("Country_code_A3")["emissions_mtco2e"].sum().mean()
    country_total = global_df[global_df["Country_code_A3"] == country_code]["emissions_mtco2e"].sum()
    return round(country_total, 2), round(global_avg, 2)

def compare_sector_with_global(df, country_code, sector_name, year):
    global_df = df[(df["year"] == year) & (df["ipcc_code_2006_for_standard_report_name"] == sector_name)]
    global_avg = global_df.groupby("Country_code_A3")["emissions_mtco2e"].sum().mean()
    country_val = global_df[global_df["Country_code_A3"] == country_code]["emissions_mtco2e"].sum()
    return round(country_val, 2), round(global_avg, 2)


def get_per_capita_emission(df_emission, df_population):
    merged = df_emission.merge(df_population, on=["Country_code_A3", "year"], how="left")
    merged["per_capita_emission"] = merged["emissions_mtco2e"] / merged["population"]
    return merged

def get_emission_per_gdp(df_emission, df_gdp, df_population):
    # Use population file to get mapping from Country → Country_code_A3
    country_map = df_population[["Country", "Country_code_A3"]].drop_duplicates()
    df_gdp = df_gdp.merge(country_map, on="Country", how="left").dropna(subset=["Country_code_A3"])

    merged = df_emission.merge(df_gdp[["Country_code_A3", "year", "gdp_billion_usd"]],
                               on=["Country_code_A3", "year"], how="left")
    merged["emission_per_gdp"] = merged["emissions_mtco2e"] / merged["gdp_billion_usd"]
    return merged