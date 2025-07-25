# Create your views here.
# dashboard/views.py
import matplotlib
matplotlib.use('Agg')  # Disable GUI backend
from django.shortcuts import render
import pandas as pd
import plotly.express as px
from datetime import datetime
import matplotlib.pyplot as plt
import io
import base64, urllib
from io import BytesIO

from dashboard.scripts.load_edgar import (
    load_edgar_ipcc2006, load_edgar_co2, load_edgar_co2bio,
    load_edgar_ch4, load_edgar_n2o
)

from dashboard.scripts.edgar_functions import emission_rank

# Load once (could be optimized later with caching)
df_ar5 = load_edgar_ipcc2006()
df_co2 = load_edgar_co2()
df_co2bio = load_edgar_co2bio()
df_ch4 = load_edgar_ch4()
df_n2o = load_edgar_n2o()

def ghg_insights(request):
    countries = sorted(df_ar5["Country_code_A3"].unique())
    years = sorted(df_ar5["year"].unique(), reverse=True)

    selected_country = request.GET.get("country", "IND")
    selected_year = int(request.GET.get("year", years[0]))

    df_sel = lambda d: d[(d["Country_code_A3"] == selected_country) & (d["year"] == selected_year)]

    total_ghg = df_sel(df_ar5)["emissions_mtco2e"].sum()
    total_co2 = df_sel(df_co2)["emissions_mtco2e"].sum()
    total_co2bio = df_sel(df_co2bio)["emissions_mtco2e"].sum()
    total_ch4 = df_sel(df_ch4)["emissions_mtco2e"].sum()
    total_n2o = df_sel(df_n2o)["emissions_mtco2e"].sum()

    rank = emission_rank(df_ar5, selected_country, selected_year)

    df_activities = df_sel(df_ar5).groupby("ipcc_code_2006_for_standard_report_name")["emissions_mtco2e"].sum().reset_index()
    df_top = df_activities.sort_values("emissions_mtco2e", ascending=False).head(10)

    fig = px.bar(
        df_top,
        x="emissions_mtco2e",
        y="ipcc_code_2006_for_standard_report_name",
        orientation="h",
        color="emissions_mtco2e",
        color_continuous_scale="Teal"
    )
    fig.update_layout(title="Top Emitting Activities", xaxis_title="Emissions (MtCO₂e)", yaxis_title="Activity")
    chart_html = fig.to_html(full_html=False)

    return render(request, 'dashboard/ghg_insights.html', {
        "countries": countries,
        "years": years,
        "selected_country": selected_country,
        "selected_year": selected_year,
        "total_ghg": total_ghg,
        "total_co2": total_co2,
        "total_co2bio": total_co2bio,
        "total_ch4": total_ch4,
        "total_n2o": total_n2o,
        "rank": rank,
        "chart_html": chart_html,
        "df_top": df_top.to_html(classes="table table-striped", index=False, float_format="%.2f")
    })


def ghg_trend_view(request):
    countries = sorted(df_ar5["Country_code_A3"].unique())
    years = sorted(df_ar5["year"].unique(), reverse=True)

    selected_country = request.GET.get("country", "IND")
    selected_year = int(request.GET.get("year", years[0]))

    df_country = df_ar5[df_ar5["Country_code_A3"] == selected_country]
    df_trend = df_country.groupby("year")["emissions_mtco2e"].sum().reset_index()

    trend_fig = px.line(df_trend, x="year", y="emissions_mtco2e",
                        title=f"GHG Emissions Over Time – {selected_country}", markers=True)
    trend_html = trend_fig.to_html(full_html=False)

    df_year = df_country[df_country["year"] == selected_year]
    df_sector = df_year.groupby("ipcc_code_2006_for_standard_report_name")["emissions_mtco2e"].sum().reset_index()
    df_top5 = df_sector.sort_values(by="emissions_mtco2e", ascending=False).head(5)

    sector_fig = px.bar(df_top5, x="emissions_mtco2e", y="ipcc_code_2006_for_standard_report_name",
                        orientation="h", color="emissions_mtco2e", color_continuous_scale="Viridis")
    sector_fig.update_layout(title="Top 5 Emitting Sectors", xaxis_title="Emissions (MtCO₂e)")
    sector_html = sector_fig.to_html(full_html=False)

    return render(request, 'dashboard/ghg_trend.html', {
        "countries": countries,
        "years": years,
        "selected_country": selected_country,
        "selected_year": selected_year,
        "trend_html": trend_html,
        "sector_html": sector_html
    })


def co2_emission_view(request):
    countries = sorted(df_co2["Country_code_A3"].unique())
    years = sorted(df_co2["year"].unique(), reverse=True)

    selected_country = request.GET.get("country", "IND")
    selected_year = int(request.GET.get("year", years[0]))

    df_country = df_co2[df_co2["Country_code_A3"] == selected_country]
    df_trend = df_country.groupby("year")["emissions_mtco2e"].sum().reset_index()

    # Line Chart
    trend_fig = px.line(
        df_trend,
        x="year",
        y="emissions_mtco2e",
        title=f"CO₂ Emissions Over Time – {selected_country}",
        markers=True
    )
    trend_html = trend_fig.to_html(full_html=False)

    # Top sectors in selected year
    df_year = df_country[df_country["year"] == selected_year]
    df_sector = df_year.groupby("ipcc_code_2006_for_standard_report_name")["emissions_mtco2e"].sum().reset_index()
    df_top5 = df_sector.sort_values(by="emissions_mtco2e", ascending=False).head(5)

    sector_fig = px.bar(
        df_top5,
        x="emissions_mtco2e",
        y="ipcc_code_2006_for_standard_report_name",
        orientation="h",
        color="emissions_mtco2e",
        color_continuous_scale="Blues"
    )
    sector_fig.update_layout(title="Top 5 CO₂ Emitting Sectors", xaxis_title="Emissions (MtCO₂e)")
    sector_html = sector_fig.to_html(full_html=False)

    return render(request, 'dashboard/co2_emission.html', {
        "countries": countries,
        "years": years,
        "selected_country": selected_country,
        "selected_year": selected_year,
        "trend_html": trend_html,
        "sector_html": sector_html
    })


def co2_bio_view(request):
    countries = sorted(df_co2bio["Country_code_A3"].unique())
    years = sorted(df_co2bio["year"].unique(), reverse=True)

    selected_country = request.GET.get("country", "IND")
    selected_year = int(request.GET.get("year", years[0]))

    df_country = df_co2bio[df_co2bio["Country_code_A3"] == selected_country]
    df_trend = df_country.groupby("year")["emissions_mtco2e"].sum().reset_index()

    # Line Chart
    trend_fig = px.line(
        df_trend,
        x="year",
        y="emissions_mtco2e",
        title=f"CO₂ (Bio) Emissions Over Time – {selected_country}",
        markers=True
    )
    trend_html = trend_fig.to_html(full_html=False)

    # Top sectors in selected year
    df_year = df_country[df_country["year"] == selected_year]
    df_sector = df_year.groupby("ipcc_code_2006_for_standard_report_name")["emissions_mtco2e"].sum().reset_index()
    df_top5 = df_sector.sort_values(by="emissions_mtco2e", ascending=False).head(5)

    sector_fig = px.bar(
        df_top5,
        x="emissions_mtco2e",
        y="ipcc_code_2006_for_standard_report_name",
        orientation="h",
        color="emissions_mtco2e",
        color_continuous_scale="Greens"
    )
    sector_fig.update_layout(title="Top 5 CO₂ (Bio) Emitting Sectors", xaxis_title="Emissions (MtCO₂e)")
    sector_html = sector_fig.to_html(full_html=False)

    return render(request, 'dashboard/co2_bio.html', {
        "countries": countries,
        "years": years,
        "selected_country": selected_country,
        "selected_year": selected_year,
        "trend_html": trend_html,
        "sector_html": sector_html
    })


def total_co2_view(request):
    countries = sorted(df_combined["Country_code_A3"].unique())
    years = sorted(df_combined["year"].unique(), reverse=True)

    selected_country = request.GET.get("country", "IND")
    selected_year = int(request.GET.get("year", years[0]))

    # Combine fossil + bio CO2
    df_combined = pd.concat([df_co2, df_co2bio])
    df_country = df_combined[df_combined["Country_code_A3"] == selected_country]
    df_trend = df_country.groupby("year")["emissions_mtco2e"].sum().reset_index()

    # Line Chart
    trend_fig = px.line(
        df_trend,
        x="year",
        y="emissions_mtco2e",
        title=f"Total CO₂ (Fossil + Bio) Emissions – {selected_country}",
        markers=True
    )
    trend_html = trend_fig.to_html(full_html=False)

    # Top sectors in selected year
    df_year = df_country[df_country["year"] == selected_year]
    df_sector = df_year.groupby("ipcc_code_2006_for_standard_report_name")["emissions_mtco2e"].sum().reset_index()
    df_top5 = df_sector.sort_values(by="emissions_mtco2e", ascending=False).head(5)

    sector_fig = px.bar(
        df_top5,
        x="emissions_mtco2e",
        y="ipcc_code_2006_for_standard_report_name",
        orientation="h",
        color="emissions_mtco2e",
        color_continuous_scale="Oranges"
    )
    sector_fig.update_layout(title="Top 5 Total CO₂ Emitting Sectors", xaxis_title="Emissions (MtCO₂e)")
    sector_html = sector_fig.to_html(full_html=False)

    return render(request, 'dashboard/total_co2.html', {
        "countries": countries,
        "years": years,
        "selected_country": selected_country,
        "selected_year": selected_year,
        "trend_html": trend_html,
        "sector_html": sector_html
    })


def ch4_emissions_view(request):
    countries = sorted(df_ch4["Country_code_A3"].unique())
    years = sorted(df_ch4["year"].unique(), reverse=True)

    selected_country = request.GET.get("country", "IND")
    selected_year = int(request.GET.get("year", years[0]))

    df_country = df_ch4[df_ch4["Country_code_A3"] == selected_country]
    df_trend = df_country.groupby("year")["emissions_mtco2e"].sum().reset_index()

    # Line Chart
    trend_fig = px.line(
        df_trend,
        x="year",
        y="emissions_mtco2e",
        title=f"CH₄ Emissions Over Time – {selected_country}",
        markers=True
    )
    trend_html = trend_fig.to_html(full_html=False)

    # Top sectors for selected year
    df_year = df_country[df_country["year"] == selected_year]
    df_sector = df_year.groupby("ipcc_code_2006_for_standard_report_name")["emissions_mtco2e"].sum().reset_index()
    df_top5 = df_sector.sort_values(by="emissions_mtco2e", ascending=False).head(5)

    sector_fig = px.bar(
        df_top5,
        x="emissions_mtco2e",
        y="ipcc_code_2006_for_standard_report_name",
        orientation="h",
        color="emissions_mtco2e",
        color_continuous_scale="Reds"
    )
    sector_fig.update_layout(title="Top 5 CH₄ Emitting Sectors", xaxis_title="Emissions (MtCO₂e)")
    sector_html = sector_fig.to_html(full_html=False)

    return render(request, 'dashboard/ch4_emissions.html', {
        "countries": countries,
        "years": years,
        "selected_country": selected_country,
        "selected_year": selected_year,
        "trend_html": trend_html,
        "sector_html": sector_html
    })


def n2o_emissions_view(request):
    countries = sorted(df_n2o["Country_code_A3"].unique())
    years = sorted(df_n2o["year"].unique(), reverse=True)

    selected_country = request.GET.get("country", "IND")
    selected_year = int(request.GET.get("year", years[0]))

    df_country = df_n2o[df_n2o["Country_code_A3"] == selected_country]
    df_trend = df_country.groupby("year")["emissions_mtco2e"].sum().reset_index()

    # Line Chart
    trend_fig = px.line(
        df_trend,
        x="year",
        y="emissions_mtco2e",
        title=f"N₂O Emissions Over Time – {selected_country}",
        markers=True
    )
    trend_html = trend_fig.to_html(full_html=False)

    # Top sectors for selected year
    df_year = df_country[df_country["year"] == selected_year]
    df_sector = df_year.groupby("ipcc_code_2006_for_standard_report_name")["emissions_mtco2e"].sum().reset_index()
    df_top5 = df_sector.sort_values(by="emissions_mtco2e", ascending=False).head(5)

    sector_fig = px.bar(
        df_top5,
        x="emissions_mtco2e",
        y="ipcc_code_2006_for_standard_report_name",
        orientation="h",
        color="emissions_mtco2e",
        color_continuous_scale="YlOrBr"
    )
    sector_fig.update_layout(title="Top 5 N₂O Emitting Sectors", xaxis_title="Emissions (MtCO₂e)")
    sector_html = sector_fig.to_html(full_html=False)

    return render(request, 'dashboard/n2o_emissions.html', {
        "countries": countries,
        "years": years,
        "selected_country": selected_country,
        "selected_year": selected_year,
        "trend_html": trend_html,
        "sector_html": sector_html
    })

def ghg_intro_view(request):
    cards = [
        {
            "title": "📋 Country Summary",
            "description": "Summarizes GHG, CO₂, CH₄, and N₂O emissions and global rank for a selected country.",
            "url": "ghg_insights",
            "color": "primary"
        },
        {
            "title": "📈 GHG Emissions",
            "description": "Shows overall GHG emission trends and top emitting sectors in a country.",
            "url": "ghg_trend",
            "color": "success"
        },
        {
            "title": "🟦 CO₂ Emission",
            "description": "Trends and top sources of fossil fuel-based CO₂ emissions.",
            "url": "co2_emission",
            "color": "info"
        },
        {
            "title": "🟩 CO₂ Bio",
            "description": "Shows CO₂ emissions from bio-based sources like land use or biomass.",
            "url": "co2_bio",
            "color": "success"
        },
        {
            "title": "🟫 Total CO₂",
            "description": "Combines fossil and bio-based CO₂ emission trends for a holistic view.",
            "url": "total_co2",
            "color": "secondary"
        },
        {
            "title": "🟥 CH₄",
            "description": "Shows methane emission trends and top sectors like agriculture or waste.",
            "url": "ch4_emissions",
            "color": "danger"
        },
        {
            "title": "🟨 N₂O",
            "description": "Shows nitrous oxide emission trends and top sectors like fertilizers.",
            "url": "n2o_emissions",
            "color": "warning"
        }
    ]
    return render(request, 'dashboard/ghg_intro.html', {"cards": cards})


gas_datasets = {
    "AR5 GHG": df_ar5,
    "CO2": df_co2,
    "CO2 Bio": df_co2bio,
    "CH4": df_ch4,
    "N2O": df_n2o,
}

def sector_summary_view(request):
    years = sorted(df_ar5["year"].unique(), reverse=True)
    countries = sorted(df_ar5["Country_code_A3"].dropna().unique())
    sectors = sorted(df_ar5["ipcc_code_2006_for_standard_report_name"].dropna().unique())

    selected_country = request.GET.get("country", "IND")
    selected_year = int(request.GET.get("year", years[0]))
    selected_sector = request.GET.get("sector", sectors[0])

    def extract_emission(df):
        return df[(df["Country_code_A3"] == selected_country) &
                  (df["year"] == selected_year) &
                  (df["ipcc_code_2006_for_standard_report_name"] == selected_sector)]["emissions_mtco2e"].sum()

    summary = {
        "AR5 GHG": extract_emission(df_ar5),  # ✅ FIXED
        "CO2": extract_emission(df_co2),
        "CO2 Bio": extract_emission(df_co2bio),
        "CH4": extract_emission(df_ch4),
        "N2O": extract_emission(df_n2o),
    }

    def get_rank(df):
        df_filtered = df[(df["year"] == selected_year) &
                         (df["ipcc_code_2006_for_standard_report_name"] == selected_sector)]
        df_rank = df_filtered.groupby("Country_code_A3")["emissions_mtco2e"].sum().reset_index()
        df_rank = df_rank.sort_values("emissions_mtco2e", ascending=False).reset_index(drop=True)
        try:
            return df_rank[df_rank["Country_code_A3"] == selected_country].index[0] + 1
        except:
            return "N/A"

    ranks = {
        "AR5 GHG": get_rank(df_ar5),  # ✅ FIXED
        "CO2": get_rank(df_co2),
        "CO2 Bio": get_rank(df_co2bio),
        "CH4": get_rank(df_ch4),
        "N2O": get_rank(df_n2o),
    }

    return render(request, "dashboard/sector_summary.html", {
        "countries": countries,
        "years": years,
        "sectors": sectors,
        "selected_country": selected_country,
        "selected_year": selected_year,
        "selected_sector": selected_sector,
        "summary": summary,
        "ranks": ranks,
    })

def sector_gas_trend_view(request, gas):
    df_gas = gas_datasets.get(gas)
    if df_gas is None:
        return render(request, "dashboard/error.html", {"message": "Invalid gas selected."})

    countries = sorted(df_gas["Country_code_A3"].dropna().unique())
    sectors = sorted(df_gas["ipcc_code_2006_for_standard_report_name"].dropna().unique())
    years = sorted(df_gas["year"].unique(), reverse=True)

    selected_country = request.GET.get("country", "IND")
    selected_sector = request.GET.get("sector", sectors[0])
    selected_year = int(request.GET.get("year", years[0]))

    df_filtered = df_gas[(df_gas["Country_code_A3"] == selected_country) &
                         (df_gas["year"] == selected_year) &
                         (df_gas["ipcc_code_2006_for_standard_report_name"] == selected_sector)]

    total_value = df_filtered["emissions_mtco2e"].sum()

    df_trend = df_gas[(df_gas["Country_code_A3"] == selected_country) &
                      (df_gas["ipcc_code_2006_for_standard_report_name"] == selected_sector)]
    df_line = df_trend.groupby("year")["emissions_mtco2e"].sum().reset_index()

    fig = px.line(df_line, x="year", y="emissions_mtco2e",
                  title=f"{gas} Trend for {selected_sector} in {selected_country}",
                  labels={"emissions_mtco2e": "Emissions (MtCO₂e)"})

    return render(request, "dashboard/sector_gas_detail.html", {
        "gas": gas,
        "selected_country": selected_country,
        "selected_sector": selected_sector,
        "selected_year": selected_year,
        "countries": countries,
        "sectors": sectors,
        "years": years,
        "total_value": total_value,
        "chart_html": fig.to_html(full_html=False)
    })


def sector_guide_view(request):
    return render(request, "dashboard/sector_guide.html")


# dashboard/views.py

from dashboard.scripts.load_edgar import load_edgar_ipcc2006
from dashboard.scripts.edgar_functions import compare_emission_trends

# Load data once
df_ar5 = load_edgar_ipcc2006()

def emission_trend_view(request):
    countries = sorted(df_ar5["Country_code_A3"].dropna().unique())
    years = sorted(df_ar5["year"].unique(), reverse=True)

    selected_countries = request.GET.getlist("countries[]") or ["IND", "USA", "CHN"]

    trend_chart = None
    warning = None

    if len(selected_countries) >= 2:
        trend_df = compare_emission_trends(df_ar5, selected_countries)

        fig, ax = plt.subplots(figsize=(10, 5))
        for country in selected_countries:
            if country in trend_df.columns:
                ax.plot(trend_df.index, trend_df[country], label=country, linewidth=2)
        ax.set_title("GHG Emission Trends Over Time")
        ax.set_xlabel("Year")
        ax.set_ylabel("Emissions (MtCO₂e)")
        ax.legend()
        fig.tight_layout()

        buf = BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        trend_chart = base64.b64encode(buf.read()).decode("utf-8")
        buf.close()
    else:
        warning = "Please select at least 2 countries for comparison."

    return render(request, "dashboard/emission_trend.html", {
        "countries": countries,
        "selected_countries": selected_countries,
        "trend_chart": trend_chart,
        "warning": warning,
    })


from dashboard.scripts.edgar_functions import compare_sector_by_country

df_ar5 = load_edgar_ipcc2006()

def sector_comparison_view(request):
    years = sorted(df_ar5["year"].unique(), reverse=True)
    sectors = sorted(df_ar5["ipcc_code_2006_for_standard_report_name"].dropna().unique())

    selected_year = int(request.GET.get("year", years[0]))
    selected_sector = request.GET.get("sector", sectors[0])

    # Data filtering and table
    sector_df = compare_sector_by_country(df_ar5, selected_sector, selected_year).head(10)

    # Generate bar chart
    chart_base64 = None
    if not sector_df.empty:
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(sector_df["Country_code_A3"], sector_df["emissions_mtco2e"], color="#FFA726")
        ax.set_ylabel("Emissions (MtCO₂e)")
        ax.set_title(f"{selected_sector} Emissions – {selected_year}")
        ax.tick_params(axis='x', rotation=45)
        fig.tight_layout()

        buf = BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        chart_base64 = base64.b64encode(buf.read()).decode("utf-8")
        buf.close()

    return render(request, "dashboard/sector_comparison.html", {
        "years": years,
        "sectors": sectors,
        "selected_year": selected_year,
        "selected_sector": selected_sector,
        "sector_df": sector_df,
        "chart_base64": chart_base64
    })

# views.py

from dashboard.scripts.edgar_functions import sector_profiles

def sector_radar_view(request):
    df = load_edgar_ipcc2006()
    years = sorted(df["year"].unique(), reverse=True)
    countries = sorted(df["Country_code_A3"].dropna().unique())

    selected_year = int(request.GET.get("year", years[0]))
    selected_countries = request.GET.getlist("countries") or ["IND", "USA"]

    radar_df = None
    chart_base64 = None

    if 2 <= len(selected_countries) <= 5:
        radar_df = sector_profiles(df, selected_countries, selected_year)

        fig, ax = plt.subplots(figsize=(12, 6))
        radar_df.plot(kind="bar", ax=ax, width=0.8)
        ax.set_ylabel("Emissions (MtCO₂e)")
        ax.set_title("Sectoral Emission Profiles")
        ax.legend(loc='upper right')
        fig.tight_layout()

        buf = BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        chart_base64 = base64.b64encode(buf.read()).decode("utf-8")
        buf.close()

    return render(request, "dashboard/sector_radar.html", {
        "years": years,
        "countries": countries,
        "selected_year": selected_year,
        "selected_countries": selected_countries,
        "radar_df": radar_df,  # <- Now checked explicitly in template
        "chart_base64": chart_base64,
    })


from dashboard.scripts.edgar_functions import stacked_sector_breakdown

def sector_stacked_view(request):
    df = load_edgar_ipcc2006()
    years = sorted(df["year"].unique(), reverse=True)
    countries = sorted(df["Country_code_A3"].dropna().unique())
    selected_year = int(request.GET.get("year", years[0]))
    selected_countries = request.GET.getlist("countries") or ["IND", "USA", "CHN"]

    stacked_df = None
    chart_base64 = None

    if selected_countries:
        stacked_df = stacked_sector_breakdown(df, selected_countries, selected_year)

        if not stacked_df.empty:
            # Sort columns by total emission
            ordered_cols = stacked_df.sum().sort_values(ascending=False).index.tolist()
            stacked_df = stacked_df[ordered_cols]

            fig, ax = plt.subplots(figsize=(12, 6))
            stacked_df.plot(kind="bar", stacked=True, ax=ax, colormap="tab20")
            ax.set_ylabel("Emissions (MtCO₂e)")
            ax.set_title("Stacked Sector Emissions – Major Contributors on Top")
            ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize="small")
            ax.tick_params(axis='x', rotation=0)
            fig.tight_layout()

            buf = BytesIO()
            fig.savefig(buf, format="png")
            buf.seek(0)
            chart_base64 = base64.b64encode(buf.read()).decode("utf-8")
            buf.close()

    return render(request, "dashboard/sector_stacked.html", {
        "years": years,
        "countries": countries,
        "selected_year": selected_year,
        "selected_countries": selected_countries,
        "stacked_df": stacked_df,
        "chart_base64": chart_base64,
    })

def emission_intelligence_view(request):
    return render(request, "dashboard/emission_intelligence.html")

from dashboard.scripts.load_edgar import load_edgar_ipcc2006, load_population, load_gdp
from dashboard.scripts.edgar_functions import (
    cumulative_emissions_n_years,
    top_growth_countries,
    compare_country_with_global,
    compare_sector_with_global,
    get_per_capita_emission,
    get_emission_per_gdp
)

# Load data globally (can cache later)
df_ar5 = load_edgar_ipcc2006()
df_pop = load_population()
df_gdp = load_gdp()

# Intro view
def deep_intro_view(request):
    return render(request, "dashboard/deep_intro.html", {"last_updated": datetime.now().strftime("%Y-%m-%d %H:%M")})

# Tab 1: Sector Analysis
def deep_sector_view(request):
    countries = sorted(df_ar5["Country_code_A3"].dropna().unique())
    years = sorted(df_ar5["year"].unique(), reverse=True)

    selected_country = request.GET.get("country", "IND")
    selected_year = int(request.GET.get("year", years[0]))

    cum_5 = cumulative_emissions_n_years(df_ar5, selected_country, selected_year, 5)
    cum_10 = cumulative_emissions_n_years(df_ar5, selected_country, selected_year, 10)
    cum_15 = cumulative_emissions_n_years(df_ar5, selected_country, selected_year, 15)

    return render(request, "dashboard/deep_sector.html", {
        "countries": countries,
        "years": years,
        "selected_country": selected_country,
        "selected_year": selected_year,
        "cum_5": cum_5,
        "cum_10": cum_10,
        "cum_15": cum_15
    })

# dashboard/views.py (continued from previous setup)

import plotly.express as px

# ------------------------------
# Tab 2: Growth Rates View
# ------------------------------
def deep_growth_view(request):
    df = load_edgar_ipcc2006()
    years = sorted(df["year"].unique(), reverse=True)
    selected_year = int(request.GET.get("year", years[0]))

    growth_charts = {}
    for n in [5, 10, 15]:
        top_growth = top_growth_countries(df, selected_year, n)
        if not top_growth.empty:
            fig = px.bar(top_growth, x="Country_code_A3", y="growth_rate",
                         labels={"growth_rate": "Growth (%)"},
                         title=f"Top 10 Growth Countries – Last {n} Years",
                         color="growth_rate",
                         color_continuous_scale="Reds")
            chart_html = fig.to_html(full_html=False)
            growth_charts[n] = chart_html

    return render(request, "dashboard/deep_growth.html", {
        "years": years,
        "selected_year": selected_year,
        "growth_charts": growth_charts
    })

# ------------------------------
# Tab 3: Country Benchmarking
# ------------------------------
def deep_country_benchmark_view(request):
    countries = sorted(df_ar5["Country_code_A3"].dropna().unique())
    years = sorted(df_ar5["year"].unique(), reverse=True)

    selected_country = request.GET.get("country", "IND")
    selected_year = int(request.GET.get("year", years[0]))

    country_val, global_avg = compare_country_with_global(df_ar5, selected_country, selected_year)
    delta = country_val - global_avg
    delta_pct = (delta / global_avg) * 100 if global_avg else 0

    return render(request, "dashboard/deep_country_benchmark.html", {
        "countries": countries,
        "years": years,
        "selected_country": selected_country,
        "selected_year": selected_year,
        "country_val": country_val,
        "global_avg": global_avg,
        "delta": delta,
        "delta_pct": delta_pct
    })

# ------------------------------
# Tab 4: Sector Benchmarking
# ------------------------------
def deep_sector_benchmark_view(request):
    df = load_edgar_ipcc2006()
    years = sorted(df["year"].unique(), reverse=True)
    sectors = sorted(df["ipcc_code_2006_for_standard_report_name"].dropna().unique())
    countries = sorted(df["Country_code_A3"].dropna().unique())

    selected_year = int(request.GET.get("year", years[0]))
    selected_sector = request.GET.get("sector", sectors[0])
    selected_country = request.GET.get("country", "IND")

    country_val, global_val = compare_sector_with_global(df, selected_country, selected_sector, selected_year)
    delta = round(country_val - global_val, 2)
    delta_pct = round((delta / global_val) * 100, 2) if global_val != 0 else 0

    return render(request, "dashboard/deep_sector_benchmark.html", {
        "years": years,
        "sectors": sectors,
        "countries": countries,
        "selected_year": selected_year,
        "selected_sector": selected_sector,
        "selected_country": selected_country,
        "country_val": country_val,
        "global_val": global_val,
        "delta": delta,
        "delta_pct": delta_pct,
    })

# ------------------------------
# Tab 5: Per Capita and GDP Efficiency
# ------------------------------
def deep_percapita_gdp_view(request):
    df = load_edgar_ipcc2006()
    df_pop = load_population()
    df_gdp = load_gdp()

    countries = sorted(df["Country_code_A3"].dropna().unique())
    selected_country = request.GET.get("country", "IND")

    df_capita = get_per_capita_emission(df, df_pop)
    df_eff = get_emission_per_gdp(df, df_gdp, df_pop)

    df_country_capita = df_capita[df_capita["Country_code_A3"] == selected_country]
    df_country_eff = df_eff[df_eff["Country_code_A3"] == selected_country]

    fig_pc = px.line(df_country_capita, x="year", y="per_capita_emission",
                     title=f"Per Capita Emissions – {selected_country}",
                     labels={"per_capita_emission": "tCO₂e/person"})

    fig_gdp = px.line(df_country_eff, x="year", y="emission_per_gdp",
                      title=f"Emissions per GDP – {selected_country}",
                      labels={"emission_per_gdp": "MtCO₂e per Billion USD"})

    return render(request, "dashboard/deep_percapita_gdp.html", {
        "countries": countries,
        "selected_country": selected_country,
        "fig_pc": fig_pc.to_html(full_html=False),
        "fig_gdp": fig_gdp.to_html(full_html=False)
    })


from dashboard.scripts.global_indicators import (
    load_zonal_temperature_data,
    load_global_temperature_data,
    get_global_annual_trend,
    get_zonal_trend_summary,
    get_temperature_rate_of_change,
    get_warming_rate_by_zone,
    load_sea_level_data,
    summarize_sea_level_trend,
    get_sea_level_trend_line,
    load_gas_data,
)

# ----------------------
# 1. Global Temperature Anomalies
# ----------------------
def global_temp_anomaly_view(request):
    df = load_global_temperature_data()
    df_annual = get_global_annual_trend(df)
    fig = px.line(df_annual, x="Year", y="Annual", title="Global Annual Temperature Anomaly (1880–Present)", markers=True)
    chart = fig.to_html(full_html=False)
    return render(request, "dashboard/global_temp_anomaly.html", {"chart": chart})

# ----------------------
# 2. Zonal Summary Table
# ----------------------
def global_zonal_summary_view(request):
    df = load_zonal_temperature_data()
    df_summary = get_zonal_trend_summary(df)
    return render(request, "dashboard/global_zonal_summary.html", {"df_table": df_summary.to_html(classes="table table-bordered", index=False)})

# ----------------------
# 3. Global Warming Rate
# ----------------------
def warming_rate_view(request):
    df = load_zonal_temperature_data()
    rate, p_value = get_temperature_rate_of_change(df)
    zonal_cols = ["Glob", "NHem", "SHem", "24N-90N", "24S-24N", "90S-24S", "64N-90N", "44N-64N", "24N-44N", "EQU-24N", "24S-EQU", "44S-24S", "64S-44S", "90S-64S"]
    zone_df = get_warming_rate_by_zone(df, zonal_cols)
    fig = px.bar(zone_df, x="zone_name", y="rate_per_decade", title="Warming Rate by Zone", color="rate_per_decade", color_continuous_scale="Plasma")
    chart = fig.to_html(full_html=False)
    return render(request, "dashboard/warming_rate.html", {"rate": round(rate, 4), "p_value": round(p_value, 4), "chart": chart})

# ----------------------
# 4. Equator vs Poles
# ----------------------
def equator_vs_poles_view(request):
    df = load_zonal_temperature_data()
    trend_zones = {
        "Equator (24S–24N)": "24S-24N",
        "Mid-North (24N–44N)": "24N-44N",
        "Mid-South (44S–24S)": "44S-24S",
        "North Pole (64N–90N)": "64N-90N",
        "South Pole (90S–64S)": "90S-64S"
    }
    fig = px.line(df, x="Year", y=[df[z] for z in trend_zones.values()], title="Temperature Anomalies: Equator vs Poles")
    for idx, (label, _) in enumerate(trend_zones.items()):
        fig.data[idx].name = label
    chart = fig.to_html(full_html=False)
    return render(request, "dashboard/equator_vs_poles.html", {"chart": chart})

# ----------------------
# 5. Sea Level View
# ----------------------
def sea_level_view(request):
    try:
        df = load_sea_level_data()
        summary = summarize_sea_level_trend(df)
        trend_df = get_sea_level_trend_line(df)
        fig = px.line(trend_df, x="time", y="sea_level_anomaly", title="Global Sea Level Anomaly")
        chart = fig.to_html(full_html=False)
        return render(request, "dashboard/sea_level.html", {
            "rate": round(summary["rate_mm_per_year"], 2),
            "total": round(summary["total_rise_mm"], 2),
            "start": summary["start_year"],
            "end": summary["end_year"],
            "chart": chart
        })
    except Exception as e:
        return render(request, "dashboard/sea_level.html", {"error": str(e)})

# ----------------------
# 6. Gas Concentration Views
# ----------------------
def gas_concentration_view(request, gas):
    gas_map = {
        "co2": ("co2_mm_gl.csv", "CO₂", "ppm"),
        "ch4": ("ch4_mm_gl.csv", "CH₄", "ppb"),
        "n2o": ("n2o_mm_gl.csv", "N₂O", "ppb"),
        "sf6": ("sf6_mm_gl.csv", "SF₆", "ppt")
    }
    if gas not in gas_map:
        return render(request, "dashboard/error.html", {"message": "Invalid gas"})

    filename, label, unit = gas_map[gas]
    df = load_gas_data(filename)

    fig1 = px.line(df, x="datetime", y="average", title=f"{label} – Global Monthly Average", labels={"average": f"{label} ({unit})"})
    fig2 = px.box(df, x="month", y="average", title=f"{label} – Monthly Seasonality", points="all")
    df_month = df.groupby("month")["average"].mean().reset_index()
    fig3 = px.line(df_month, x="month", y="average", title=f"{label} – Avg by Month")

    return render(request, "dashboard/gas_concentration.html", {
        "label": label,
        "unit": unit,
        "fig1": fig1.to_html(full_html=False),
        "fig2": fig2.to_html(full_html=False),
        "fig3": fig3.to_html(full_html=False)
    })

def global_trends_home(request):
    return render(request, "dashboard/global_trends.html")


from dashboard.scripts.electricity_insights import (
    load_power_plant_data,
    get_country_plant_data,
    get_total_capacity,
    get_fuel_mix_distribution,
    get_fuel_capacity_distribution,
    get_location_map_df,
    capacity_over_time,
    average_capacity_by_fuel,
    generation_efficiency,
    fuel_mix_over_time,
)

def electricity_intro_view(request):
    return render(request, "dashboard/electricity_intro.html")

def electricity_summary_view(request):
    df = load_power_plant_data()
    countries = sorted(df['country'].dropna().unique())
    selected_country = request.GET.get("country", "IND")

    df_country = get_country_plant_data(df, selected_country)
    total_capacity = get_total_capacity(df_country)

    table_html = df_country[["name", "capacity_mw", "primary_fuel", "commissioning_year"]] \
        .sort_values(by="capacity_mw", ascending=False) \
        .to_html(classes="table table-bordered table-striped", index=False)

    return render(request, "dashboard/electricity_summary.html", {
        "countries": countries,
        "selected_country": selected_country,
        "total_capacity": f"{total_capacity:,.2f}",
        "table_html": table_html
    })

import plotly.express as px

def electricity_fuel_mix_view(request):
    df = load_power_plant_data()
    countries = sorted(df['country'].dropna().unique())
    selected_country = request.GET.get("country", "IND")

    df_country = get_country_plant_data(df, selected_country)

    fuel_mix_pct = get_fuel_mix_distribution(df_country)
    fuel_mix_cap = get_fuel_capacity_distribution(df_country)

    # Pie Chart for plant count distribution
    fig1 = px.pie(
        fuel_mix_pct,
        names="Fuel_Type",     # Correct name column
        values="proportion",   # Correct numerical value column
        title="Fuel Mix – Plant Count (%)"
        )
        
    # Bar Chart for installed capacity by fuel
    fig2 = px.bar(
        fuel_mix_cap,
        x="primary_fuel",
        y="capacity_mw",
        title="Fuel Mix – Installed Capacity (MW)",
        labels={"capacity_mw": "MW", "primary_fuel": "Fuel"},
        text_auto=".2s"
    )

    return render(request, "dashboard/electricity_fuel_mix.html", {
        "countries": countries,
        "selected_country": selected_country,
        "fig1": fig1.to_html(full_html=False),
        "fig2": fig2.to_html(full_html=False)
    })


def electricity_map_view(request):
    df = load_power_plant_data()
    countries = sorted(df['country'].dropna().unique())
    selected_country = request.GET.get("country", "IND")

    df_country = get_country_plant_data(df, selected_country)
    map_df = get_location_map_df(df_country)

    fig = px.scatter_mapbox(
        map_df,
        lat="latitude",
        lon="longitude",
        color="primary_fuel",
        size="capacity_mw",
        hover_name="name",
        zoom=3,
        height=600,
        mapbox_style="open-street-map",
        title=f"📍 Power Plants in {selected_country}"
    )

    chart = fig.to_html(full_html=False)

    return render(request, "dashboard/electricity_map.html", {
        "countries": countries,
        "selected_country": selected_country,
        "chart": chart
    })


def electricity_capacity_trend_view(request):
    df = load_power_plant_data()
    countries = sorted(df["country"].dropna().unique())
    selected_country = request.GET.get("country", "IND")

    df_country = get_country_plant_data(df, selected_country)
    cap_time_df = capacity_over_time(df_country)

    fig = px.line(
        cap_time_df,
        x="commissioning_year",
        y="capacity_mw",
        title=f"📈 Installed Capacity Over Time – {selected_country}",
        markers=True,
        labels={"commissioning_year": "Year", "capacity_mw": "MW"},
        height=500
    )

    chart = fig.to_html(full_html=False)

    return render(request, "dashboard/electricity_capacity_trend.html", {
        "countries": countries,
        "selected_country": selected_country,
        "chart": chart
    })


def electricity_avg_capacity_view(request):
    df = load_power_plant_data()
    countries = sorted(df["country"].dropna().unique())
    selected_country = request.GET.get("country", "IND")

    df_country = get_country_plant_data(df, selected_country)
    avg_df = average_capacity_by_fuel(df_country)

    fig = px.bar(
        avg_df,
        x="primary_fuel",
        y="avg_capacity_mw",
        title=f"📊 Average Plant Capacity by Fuel – {selected_country}",
        labels={"primary_fuel": "Fuel Type", "avg_capacity_mw": "MW"},
        height=500
    )

    chart = fig.to_html(full_html=False)

    return render(request, "dashboard/electricity_avg_capacity.html", {
        "countries": countries,
        "selected_country": selected_country,
        "chart": chart
    })

def electricity_efficiency_view(request):
    df = load_power_plant_data()
    countries = sorted(df["country"].dropna().unique())
    selected_country = request.GET.get("country", "IND")
    all_years = [2013, 2014, 2015, 2016, 2017]

    df_country = get_country_plant_data(df, selected_country)

    # Filter years for which both columns exist and contain data
    available_years = [
        y for y in all_years
        if f"generation_gwh_{y}" in df_country.columns and
           f"estimated_generation_gwh_{y}" in df_country.columns and
           not df_country[[f"generation_gwh_{y}", f"estimated_generation_gwh_{y}"]].dropna().empty
    ]

    # Fallback: if no data, use full list
    if not available_years:
        available_years = all_years

    selected_year = int(request.GET.get("year", available_years[0]))

    chart = None
    table_html = None

    try:
        gen_df = generation_efficiency(df_country, year=selected_year)
        if not gen_df.empty:
            fig = px.scatter(
                gen_df,
                x=f"estimated_generation_gwh_{selected_year}",
                y=f"generation_gwh_{selected_year}",
                color="primary_fuel",
                size="utilization_ratio",
                hover_name="name",
                title=f"Generation Efficiency – {selected_year}"
            )
            chart = fig.to_html(full_html=False)
            table_html = gen_df.to_html(classes="table table-striped", index=False)
    except Exception:
        pass

    return render(request, "dashboard/electricity_efficiency.html", {
        "countries": countries,
        "selected_country": selected_country,
        "selected_year": selected_year,
        "years": available_years,
        "chart": chart,
        "table_html": table_html,
    })


def electricity_fuel_mix_time_view(request):
    df = load_power_plant_data()
    countries = sorted(df["country"].dropna().unique())
    selected_country = request.GET.get("country", "IND")

    df_country = get_country_plant_data(df, selected_country)
    mix_df = fuel_mix_over_time(df_country)

    fig = px.area(
        mix_df,
        x="commissioning_year",
        y="capacity_mw",
        color="primary_fuel",
        title=f"📊 Fuel Mix Evolution Over Time – {selected_country}",
        labels={"commissioning_year": "Year", "capacity_mw": "MW", "primary_fuel": "Fuel"}
    )

    chart = fig.to_html(full_html=False)

    return render(request, "dashboard/electricity_fuel_mix_time.html", {
        "countries": countries,
        "selected_country": selected_country,
        "chart": chart,
    })

def electricity_about_view(request):
    return render(request, "dashboard/electricity_about.html")


# dashboard/views.py

import os

from django.conf import settings

DATA_PATH = os.path.join(settings.BASE_DIR, 'data')

from dashboard.scripts.owid_functions import (
    renewable_share_over_time,
    renewable_source_breakdown,
    top_countries_by_renewable,
    fastest_growth_in_renewables,
    electricity_mix,
)

# Load OWID data (cached in memory for all views)

df_owid = pd.read_csv(os.path.join(DATA_PATH, "owid-energy-data.csv"))

def renewable_intro_view(request):
    return render(request, "dashboard/renewable_intro.html")

# dashboard/views.py (additional views for renewable module)

# 1. Trend over time

def renewable_trend_view(request):
    countries = sorted(df_owid["iso_code"].dropna().unique())
    selected_country = request.GET.get("country", "IND")
    trend = renewable_share_over_time(df_owid, selected_country)

    chart = None
    if not trend.empty:
        fig = px.line(trend, x="year", y="renewables_share_energy",
                      title=f"Renewable Energy Share Over Time – {selected_country}",
                      labels={"renewables_share_energy": "Renewable Share (%)", "year": "Year"})
        chart = fig.to_html(full_html=False)

    context = {
        "countries": countries,
        "selected_country": selected_country,
        "chart": chart,  # <-- pass this
    }
    return render(request, "dashboard/renewable_trend.html", context)

# 2. Source Breakdown

def renewable_source_breakdown_view(request):
    countries = sorted(df_owid["iso_code"].dropna().unique())
    years = sorted(df_owid["year"].dropna().unique(), reverse=True)
    selected_country = request.GET.get("country", "IND")
    selected_year = int(request.GET.get("year", max(years)))

    share = renewable_source_breakdown(df_owid, selected_country, selected_year)
    chart = None
    if share:
        fig, ax = plt.subplots()
        ax.pie(share.values(), labels=share.keys(), autopct="%1.1f%%", startangle=90)
        ax.set_title("Renewable Source Breakdown")
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        chart = base64.b64encode(buf.read()).decode("utf-8")
        buf.close()
    return render(request, "dashboard/renewable_source_breakdown.html", {
        "countries": countries,
        "years": years,
        "selected_country": selected_country,
        "selected_year": selected_year,
        "chart": chart
    })

# 3. Top Countries by Renewable Share

def renewable_top_countries_view(request):
    years = sorted(df_owid["year"].dropna().unique(), reverse=True)
    selected_year = int(request.GET.get("year", max(years)))
    top_df = top_countries_by_renewable(df_owid, selected_year)
    return render(request, "dashboard/renewable_top_countries.html", {
        "years": years,
        "selected_year": selected_year,
        "table_html": top_df.to_html(classes="table table-striped", index=False)
    })

# 4. Fastest Growth

def renewable_fastest_growth_view(request):
    years = sorted(df_owid["year"].dropna().unique())
    start_year = int(request.GET.get("start", 2000))
    end_year = int(request.GET.get("end", max(years)))
    growth_df = fastest_growth_in_renewables(df_owid, start_year, end_year)
    return render(request, "dashboard/renewable_fastest_growth.html", {
        "years": years,
        "start_year": start_year,
        "end_year": end_year,
        "table_html": growth_df.to_html(classes="table table-bordered", index=False)
    })

# 5. Electricity Mix

def renewable_electricity_mix_view(request):
    countries = sorted(df_owid["iso_code"].dropna().unique())
    years = sorted(df_owid["year"].dropna().unique(), reverse=True)
    selected_country = request.GET.get("country", "IND")
    selected_year = int(request.GET.get("year", max(years)))

    mix = electricity_mix(df_owid, selected_country, selected_year)
    chart = None
    if mix:
        fig, ax = plt.subplots()
        ax.bar(mix.keys(), mix.values(), color=["gray", "green"])
        ax.set_title(f"{selected_country} Electricity Mix – {selected_year}")
        ax.set_ylabel("Electricity (TWh)")
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        chart = base64.b64encode(buf.read()).decode("utf-8")
        buf.close()

    return render(request, "dashboard/renewable_electricity_mix.html", {
        "countries": countries,
        "years": years,
        "selected_country": selected_country,
        "selected_year": selected_year,
        "chart": chart
    })

from dashboard.scripts.displacement_analysis import (
    fossil_vs_renewable_energy,
    energy_growth_rates,
    energy_shares,
    displacement_score,
)

OWID_PATH = os.path.join(settings.BASE_DIR, "data", "owid-energy-data.csv")
df = pd.read_csv(OWID_PATH)
countries = sorted(df["iso_code"].dropna().unique())


def displacement_intro_view(request):
    return render(request, "dashboard/displacement_intro.html")


def displacement_fossil_vs_renewable_view(request):
    selected_country = request.GET.get("country", "IND")
    data = fossil_vs_renewable_energy(df, selected_country)
    fig = px.line(
        data,
        x="year",
        y=["fossil_energy", "renewables_energy"],
        title=f"Fossil vs Renewable Energy – {selected_country}"
    )
    chart = fig.to_html(full_html=False)
    return render(request, "dashboard/displacement_fossil_vs_renewable.html", {
        "chart": chart,
        "countries": countries,
        "selected_country": selected_country
    })


def displacement_growth_rate_view(request):
    selected_country = request.GET.get("country", "IND")
    data = energy_growth_rates(df, selected_country)
    fig = px.line(
        data,
        x="year",
        y=["fossil_growth", "renewable_growth"],
        title=f"Annual Growth Rate – {selected_country}"
    )
    chart = fig.to_html(full_html=False)
    return render(request, "dashboard/displacement_growth_rate.html", {
        "chart": chart,
        "countries": countries,
        "selected_country": selected_country
    })


def displacement_energy_share_view(request):
    selected_country = request.GET.get("country", "IND")
    data = energy_shares(df, selected_country)
    fig = px.line(
        data,
        x="year",
        y=["fossil_share", "renewable_share"],
        title=f"Energy Share in Total Mix – {selected_country}"
    )
    chart = fig.to_html(full_html=False)
    return render(request, "dashboard/displacement_energy_share.html", {
        "chart": chart,
        "countries": countries,
        "selected_country": selected_country
    })


def displacement_score_view(request):
    import matplotlib.pyplot as plt
    import io
    import base64

    selected_country = request.GET.get("country", "IND")
    data = displacement_score(df, selected_country)

    fig, ax = plt.subplots()
    ax.plot(data["year"], data["displacement_score"], color="green")
    ax.axhline(0, linestyle="--", color="gray")
    ax.set_ylabel("Displacement Score (%)")
    ax.set_xlabel("Year")
    ax.set_title(f"{selected_country}: Displacement Effectiveness Over Time")

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    chart = base64.b64encode(buf.read()).decode("utf-8")
    buf.close()

    return render(request, "dashboard/displacement_score.html", {
        "chart": chart,
        "countries": countries,
        "selected_country": selected_country
    })


def displacement_guide_view(request):
    return render(request, "dashboard/displacement_guide.html")

def dashboard_overview(request):
    dashboards = [
        {
            "title": "GHG Insights",
            "url": "dashboard:ghg_insights",
            "description": "Overview of greenhouse gas emissions globally and by country."
        },
        {
            "title": "GHG Trend",
            "url": "dashboard:ghg_trend",
            "description": "Trend analysis of major greenhouse gases over time."
        },
        {
            "title": "CO2 Emissions",
            "url": "dashboard:co2_emission",
            "description": "Carbon dioxide emissions breakdown by country and sector."
        },
        {
            "title": "CO2 Bio Emissions",
            "url": "dashboard:co2_bio",
            "description": "Biogenic CO2 emissions from natural and agricultural sources."
        },
        {
            "title": "Total CO2",
            "url": "dashboard:total_co2",
            "description": "Total carbon emissions including fossil, bio, and other sources."
        },
        {
            "title": "Methane (CH₄)",
            "url": "dashboard:ch4_emissions",
            "description": "Methane emissions data with sector-wise trends."
        },
        {
            "title": "Nitrous Oxide (N₂O)",
            "url": "dashboard:n2o_emissions",
            "description": "Nitrous oxide emissions with agriculture and industrial sources."
        },
        {
            "title": "Global Temperature Trends",
            "url": "dashboard:global_temp_anomaly",
            "description": "Global warming temperature anomaly trends since 1880."
        },
        {
            "title": "Sea Level Rise",
            "url": "dashboard:sea_level",
            "description": "Trends and analysis of global sea level rise over time."
        },
        {
            "title": "Renewable Energy Trends",
            "url": "dashboard:renewable_trend",
            "description": "Growth and patterns of renewable energy usage worldwide."
        },
        # Add more dashboards as needed...
    ]
    return render(request, 'dashboard/overview.html', {"dashboards": dashboards})


def about_view(request):
    return render(request, 'dashboard/about.html')

def mission_view(request):
    return render(request, 'dashboard/mission.html')

def careers_view(request):
    return render(request, 'dashboard/careers.html')

def what_we_do_view(request):
    return render(request, 'dashboard/what_we_do.html')

def our_team_view(request):
    return render(request, 'dashboard/team.html')

