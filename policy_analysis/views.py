import os
import json
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Policy, PolicySection
from .relationship_logic import create_relationships_for_new_policy
from .models import PolicyRelationship
from django.db.models import Q, F

# Helper to extract unique values from list fields
def extract_unique_json_values(queryset, field):
    values = set()
    for obj in queryset:
        items = getattr(obj, field, [])
        if isinstance(items, list):
            for item in items:
                if isinstance(item, str):
                    parts = [p.strip().lower() for p in item.split(',')]
                    values.update(parts)
    return sorted(values)


def policy_home(request):
    return render(request, 'policy_analysis/home.html')

def policy_graph_home(request):
    return render(request, 'policy_analysis/policy_graph_home.html')


def parse_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except Exception as e:
        print(f"Date parse error: {e}")
        return None


def upload_metadata(request):
    if request.method == 'POST':
        policy_file = request.FILES.get('policy_file')
        section_file = request.FILES.get('section_file')

        if not policy_file or not section_file:
            messages.error(request, "Both files are required.")
            return redirect('upload_metadata')

        try:
            policy_data = json.load(policy_file)
            section_data = json.load(section_file)
        except json.JSONDecodeError:
            messages.error(request, "Uploaded files must be valid JSON.")
            return redirect('upload_metadata')

        policy_obj, _ = Policy.objects.update_or_create(
            policy_id=policy_data['policy_id'],
            defaults={
                'title': policy_data.get('title', '').strip().title(),
                'summary': policy_data.get('summary', ''),
                'year': policy_data.get('year', 2000),
                'date_of_issuance': parse_date(policy_data.get('date_of_issuance', '2000-01-01')),
                'country': policy_data.get('country', 'NA'),
                'document_type': policy_data.get('document_type', 'Unknown'),
                'is_fundamental': policy_data.get('is_fundamental', False),
                'has_children': policy_data.get('has_children', False),
                'num_sections': policy_data.get('num_sections', 0),
                'sectors': policy_data.get('sectors', []),
                'sub_sectors': policy_data.get('sub_sectors', []),
                'intent_tags': policy_data.get('intent_tags', []),
                'policy_tools': policy_data.get('policy_tools', []),
                'responsible_ministries': policy_data.get('responsible_ministries', []),
                'linked_documents': policy_data.get('linked_documents', []),
            }
        )

        for sec in section_data:
            PolicySection.objects.update_or_create(
                section_id=sec['section_id'],
                defaults={
                    'policy': policy_obj,
                    'title': sec.get('title', ''),
                    'summary': sec.get('summary', ''),
                    'sector': sec.get('sector', ''),
                    'sub_sectors': sec.get('sub_sectors', []),
                    'intent_tags': sec.get('intent_tags', []),
                    'policy_type': sec.get('policy_type', ''),
                    'policy_tools': sec.get('policy_tools', []),
                    'responsible_ministries': sec.get('responsible_ministries', []),
                    'linked_documents': sec.get('linked_documents', []),
                    'global_alignment': sec.get('global_alignment', ''),
                    'is_legally_binding': str(sec.get('is_legally_binding', '')),
                    'compliance_type': sec.get('compliance_type', ''),
                    'mrv_system': sec.get('mrv_system', ''),
                    'monitoring_mechanism': sec.get('monitoring_mechanism', ''),
                    'targets': str(sec.get('targets', '')),
                    'impact_estimate': str(sec.get('impact_estimate', '')),
                    'climate_finance': str(sec.get('climate_finance', '')),
                    'financial_outlay': str(sec.get('financial_outlay', '')),
                    'yearly_budget': str(sec.get('yearly_budget', '')),
                    'timeline': sec.get('timeline', ''),
                    'lifecycle_history': sec.get('lifecycle_history', ''),
                    'kpis': str(sec.get('kpis', '')),
                    'linked_ndcs_or_sdgs': str(sec.get('linked_ndcs_or_sdgs', '')),
                }
            )

        # ✅ Auto-generate relationships for the new policy
        create_relationships_for_new_policy(policy_obj)

        messages.success(request, f"{policy_obj.title} uploaded with {len(section_data)} sections.")
        return redirect('upload_metadata')

    return render(request, 'policy_analysis/upload.html')

def clean_policy_title(raw_title):
    # Remove leading 'policy_COUNTRY_DATE_' prefix
    parts = raw_title.split('_')
    if len(parts) > 4 and parts[0].lower() == 'policy':
        return ' '.join(parts[4:]).replace('(', ' (').replace(')', ')').strip().title()
    return raw_title.replace('_', ' ').title()


def explore_metadata(request):
    country = request.GET.get('country', '').strip()
    year = request.GET.get('year', '').strip()
    sector = request.GET.get('sector', '').strip()

    policies = list(Policy.objects.all())

    if country:
        policies = [p for p in policies if p.country.lower() == country.lower()]

    if year:
        try:
            y = int(year)
            policies = [p for p in policies if p.year == y]
        except ValueError:
            pass

    if sector:
        sector_lower = sector.lower()
        policies = [p for p in policies if p.sectors and any(sector_lower in s.lower() for s in p.sectors)]

    countries = Policy.objects.values_list('country', flat=True).distinct()
    years = Policy.objects.values_list('year', flat=True).distinct()

    context = {
        'policies': policies,
        'countries': countries,
        'years': years,
    }

    return render(request, 'policy_analysis/explore.html', context)


def policy_detail(request, policy_id):
    policy = Policy.objects.get(policy_id=policy_id)
    sections = PolicySection.objects.filter(policy=policy)

    context = {
        'policy': policy,
        'sections': sections,
    }

    return render(request, 'policy_analysis/policy_detail.html', context)


def generate_abbreviation(title):
    words = title.replace('_', ' ').split()
    clean_words = [w for w in words if w and not w.isdigit() and not w[:4].isdigit()]
    abbrev = ''.join([w[0].upper() for w in clean_words if w[0].isalpha()])
    return abbrev[:4]

def policy_graph_view(request):
    country = request.GET.get("country")
    min_score = float(request.GET.get("score", 0))
    sector = request.GET.get("sector")
    ministry = request.GET.get("ministry")
    compliance = request.GET.get("compliance")

    relationships = PolicyRelationship.objects.select_related('parent_policy', 'child_policy')

    if country:
        relationships = relationships.filter(
            parent_policy__country=country,
            child_policy__country=country
        )

    if min_score:
        relationships = relationships.filter(similarity_score__gte=min_score)

    if sector:
        relationships = relationships.filter(
            Q(parent_policy__sectors__icontains=sector) |
            Q(child_policy__sectors__icontains=sector)
        )

    if ministry:
        relationships = relationships.filter(
            Q(parent_policy__responsible_ministries__icontains=ministry) |
            Q(child_policy__responsible_ministries__icontains=ministry)
        )

    if compliance:
        relationships = relationships.filter(
            Q(parent_policy__sections__compliance_type__icontains=compliance) |
            Q(child_policy__sections__compliance_type__icontains=compliance)
        ).distinct()

    nodes_dict = {}
    links = []
    seen_edges = set()

    for rel in relationships:
        parent_id = rel.parent_policy.policy_id
        child_id = rel.child_policy.policy_id

        edge_key = tuple(sorted([parent_id, child_id]))
        if edge_key in seen_edges:
            continue
        seen_edges.add(edge_key)

        if parent_id not in nodes_dict:
            full_title = clean_policy_title(rel.parent_policy.title)
            abbrev = generate_abbreviation(full_title)
            nodes_dict[parent_id] = {
                "id": parent_id,
                "title": full_title,
                "label": abbrev,
                "url": f"/analysis/explore/{parent_id}/",
                "group": 1
            }

        if child_id not in nodes_dict:
            full_title = clean_policy_title(rel.child_policy.title)
            abbrev = generate_abbreviation(full_title)
            nodes_dict[child_id] = {
                "id": child_id,
                "title": full_title,
                "label": abbrev,
                "url": f"/analysis/explore/{child_id}/",
                "group": 1
            }

        links.append({
            "source": parent_id,
            "target": child_id,
            "type": rel.relationship_type,
            "score": rel.similarity_score
        })

    all_policies = Policy.objects.all()
    all_sections = PolicySection.objects.all()

    unique_sectors = extract_unique_json_values(all_policies, "sectors")
    unique_ministries = extract_unique_json_values(all_policies, "responsible_ministries")
    unique_compliance_types = sorted(set(filter(None, all_sections.values_list('compliance_type', flat=True))))

    legend_items = sorted([
        {"abbr": n["label"], "title": n["title"]} for n in nodes_dict.values()
    ], key=lambda x: x["abbr"])

    context = {
        "nodes_json": json.dumps(list(nodes_dict.values())),
        "links_json": json.dumps(links),
        "legend": legend_items,
        "country": country,
        "sector": sector,
        "ministry": ministry,
        "compliance": compliance,
        "score": min_score,
        "sector_choices": unique_sectors,
        "ministry_choices": unique_ministries,
        "compliance_choices": unique_compliance_types,
    }

    return render(request, 'policy_analysis/policy_graph.html', context)
