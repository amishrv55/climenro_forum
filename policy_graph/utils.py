import pandas as pd
import re

def load_activity_table(path='data/activity_emission_factor.csv'):
    df = pd.read_csv(path, encoding='utf-8')
    df['Keywords'] = df['Keywords'].fillna('').apply(
        lambda x: [kw.strip().lower() for kw in x.split(',')]
    )
    return df

def load_country_factors(path='data/country_composite_factor.csv'):
    df = pd.read_csv(path, encoding='utf-8')
    df['Country'] = df['Country'].str.strip()
    return df

def get_displacement_ratio(country_name, df_country):
    row = df_country[df_country['Country'].str.lower() == country_name.lower()]
    if not row.empty:
        return float(row.iloc[0]['Displacement Ratio'])
    return None  # Or raise warning

def classify_policy(policy_text, df_activity):
    policy_text = policy_text.lower()
    match_scores = []

    for idx, row in df_activity.iterrows():
        # Ensure keywords are in list form
        keywords = row['Keywords']
        if isinstance(keywords, str):
            keywords = [kw.strip().lower() for kw in keywords.split(',')]
        elif isinstance(keywords, list):
            keywords = [kw.strip().lower() for kw in keywords]
        else:
            keywords = []

        score = sum(1 for kw in keywords if kw in policy_text)
        match_scores.append(score)

    best_idx = pd.Series(match_scores).idxmax()

    if match_scores[best_idx] == 0:
        return {"matched": False, "activity_class": None}

    row = df_activity.loc[best_idx]
    matched_keywords = row['Keywords']
    if isinstance(matched_keywords, str):
        matched_keywords = [kw.strip().lower() for kw in matched_keywords.split(',') if kw.strip().lower() in policy_text]
    elif isinstance(matched_keywords, list):
        matched_keywords = [kw.strip().lower() for kw in matched_keywords if kw.strip().lower() in policy_text]
    else:
        matched_keywords = []

    return {
        "matched": True,
        "match_index": best_idx,
        "activity_class": row['Activity Class'],
        "keywords_matched": matched_keywords,
        "emission_per_unit": row['CO₂e Impact'],
        "unit": row['Unit'],
        "instrument_type": row['Instrument Type'],
        "sector": row['Sector']
    }


def estimate_emission_impact(policy_result, budget, subsidy_per_unit, displacement_ratio):
    try:
        # Parse emission value from policy_result['emission_per_unit'] like '–1.6 tons'
        emission_value = float(policy_result['emission_per_unit'].replace('–', '-').split()[0])
        estimated_units = budget / subsidy_per_unit
        total_impact = estimated_units * emission_value * displacement_ratio
        return round(total_impact, 2)
    except Exception as e:
        return None

def parse_emission_value(emission_str):
    try:
        return float(emission_str.replace('–', '-').replace(',', '').split()[0])
    except Exception:
        return None

def get_required_input_type(activity_row):
    if isinstance(activity_row, pd.Series):
        return activity_row.get('Required Input Type', 'budget').strip().lower()
    return 'budget'

def estimate_units(policy_row, user_input, country_row=None):
    input_type = get_required_input_type(policy_row)
    
    if input_type == 'budget':
        unit_cost = policy_row.get('Default Unit Cost')
        if pd.isna(unit_cost) or unit_cost == 0:
            return None
        displacement_ratio = 1.0
        if country_row is not None and policy_row.get('Uses Displacement', False):
            displacement_ratio = float(country_row.get('Displacement Ratio', 1.0))
        return (user_input / float(unit_cost)) * displacement_ratio
    
    else:
        # For other direct quantity inputs (length, area, etc.)
        return user_input

def estimate_emission_impact(policy_row, user_input, country_row=None):
    emission_per_unit = parse_impact_to_float(policy_row.get('CO₂e Impact', ''))
    if emission_per_unit is None:
        return None

    units = estimate_units(policy_row, user_input, country_row)
    if units is None:
        return None

    return round(units * emission_per_unit, 2)

def get_activity_row(policy_result, df_activity):
    return df_activity[df_activity['Activity Class'] == policy_result['activity_class']].iloc[0]

def build_policy_node(policy_text, country, budget, subsidy_per_unit=5000, df_activity=None, df_country=None):
    result = classify_policy(policy_text, df_activity)
    displacement_ratio = get_displacement_ratio(country, df_country)

    if not result["matched"] or not displacement_ratio:
        return None

    activity_row = get_activity_row(result, df_activity)
    country_row = df_country[df_country['Country'].str.lower() == country.lower()].iloc[0]
    total_impact = estimate_emission_impact(activity_row, budget, country_row)
    emission_value = parse_emission_value(result['emission_per_unit'])

    alignment = "Positive" if emission_value < 0 else "Negative" if emission_value > 0 else "Neutral"
    node_color = "green" if alignment == "Positive" else "red" if alignment == "Negative" else "gray"
    node_size = min(max(abs(total_impact), 10), 100)

    # Safe efficiency extraction with fallback
    efficiency = country_row["Efficiency"] if "Efficiency" in country_row else 1.0

    return {
        "Policy Node": result["activity_class"],
        "Core Intent": result["activity_class"],
        "Sector": result["sector"],
        "Dept": sector_to_dept(result["sector"]),
        "CO₂ Impact (Mt ±)": round(total_impact / 1e6, 4) if total_impact else None,
        "Impact Factor": round(total_impact / 1e6, 4) if total_impact else None,
        "Alignment": alignment,
        "Instrument": result.get("instrument_type", "Subsidy"),
        "Start–End": "2025–2030",
        "Beneficiary": sector_to_beneficiary(result["sector"]),
        "Influencer": sector_to_influencer(result["sector"]),
        "Efficiency": efficiency,
        "Node Size": node_size,
        "Node Color": node_color
    }


def sector_to_dept(sector):
    mapping = {
        "Transport": "Ministry of Transport",
        "Electricity": "Ministry of Energy",
        "Cement": "Ministry of Industry",
        "Agriculture": "Ministry of Agriculture",
        "Waste": "Urban Development",
        # Add more...
    }
    return mapping.get(sector, "General")

def sector_to_beneficiary(sector):
    mapping = {
        "Transport": "Urban Citizens",
        "Cement": "Cement Companies",
        "Electricity": "Power Producers",
        # ...
    }
    return mapping.get(sector, "Public")

def sector_to_influencer(sector):
    mapping = {
        "Transport": "UNEP, EV Lobbies",
        "Cement": "IPCC, Carbon Funders",
        "Electricity": "Renewable Advocates",
        # ...
    }
    return mapping.get(sector, "General Influencers")

def get_efficiency_score(country, df_country):
    row = df_country[df_country['Country'].str.lower() == country.lower()]
    if not row.empty:
        return float(row.iloc[0]['Efficiency'])
    return 0.5

def parse_impact_to_float(impact_str):
    try:
        # Replace en-dash with minus, remove commas and units
        clean = impact_str.replace("–", "-").replace(",", "")
        number_part = re.findall(r"-?\d+\.?\d*", clean)
        return float(number_part[0]) if number_part else 0.0
    except Exception:
        return 0.0
