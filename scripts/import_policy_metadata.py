import sys
import os
import django
import json
from datetime import datetime

# Add BASE_DIR to Python path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Set DJANGO_SETTINGS_MODULE
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "climenro_forum_app.settings")

# Initialize Django
django.setup()

from policy_analysis.models import Policy, PolicySection

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except:
        return None

def import_metadata(policy_file, section_file):
    with open(policy_file, 'r', encoding='utf-8') as f1:
        policy_data = json.load(f1)

    with open(section_file, 'r', encoding='utf-8') as f2:
        section_data = json.load(f2)

    # Create or update the policy
    policy_obj, created = Policy.objects.update_or_create(
        policy_id=policy_data['policy_id'],
        defaults={
            'title': policy_data.get('title'),
            'summary': policy_data.get('summary') or '',
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

    # Create/update sections
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

    print(f"✅ Imported {policy_obj.title} with {len(section_data)} sections.")


if __name__ == "__main__":
    policy_file_path = 'data/policy_metadata_NAPCC.txt'
    section_file_path = 'data/section_Metadata_NPCC.txt'

    import_metadata(policy_file_path, section_file_path)
