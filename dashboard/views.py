# Create your views here.
# dashboard/views.py
from django.shortcuts import render
import pandas as pd
import plotly.express as px
from datetime import datetime

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
    countries = sorted(df["Country_code_A3"].unique())
    years = sorted(df["year"].unique(), reverse=True)

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
    countries = sorted(df["Country_code_A3"].unique())
    years = sorted(df["year"].unique(), reverse=True)

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
    countries = sorted(df["Country_code_A3"].unique())
    years = sorted(df["year"].unique(), reverse=True)

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
    countries = sorted(df["Country_code_A3"].unique())
    years = sorted(df["year"].unique(), reverse=True)

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
    countries = sorted(df["Country_code_A3"].unique())
    years = sorted(df["year"].unique(), reverse=True)

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
