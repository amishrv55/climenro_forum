from rapidfuzz import fuzz
from policy_analysis.models import Policy, PolicyRelationship
from django.db.models import Q

def compute_similarity_score(policy1, policy2):
    score = 0
    if policy1.country == policy2.country:
        score += 0.2

    # Title similarity
    score += fuzz.token_sort_ratio(policy1.title, policy2.title) / 100 * 0.4

    # Policy tools overlap
    common_tools = set(policy1.policy_tools or []).intersection(set(policy2.policy_tools or []))
    score += len(common_tools) / max(len(policy1.policy_tools or []), 1) * 0.2

    # Intent tags overlap
    common_tags = set(policy1.intent_tags or []).intersection(set(policy2.intent_tags or []))
    score += len(common_tags) / max(len(policy1.intent_tags or []), 1) * 0.2

    return round(score, 2)

def infer_relationship_type(policy1, policy2):
    if policy2.date_of_issuance and policy1.date_of_issuance:
        if policy2.date_of_issuance > policy1.date_of_issuance:
            return 'revision_of'
    return 'related_to'

def build_relationships():
    policies = list(Policy.objects.all())
    print(f"\n📌 Found {len(policies)} policies.\n")

    created_count = 0

    for i, p1 in enumerate(policies):
        for j, p2 in enumerate(policies):
            if i == j:
                continue

            score = compute_similarity_score(p1, p2)
            print(f"🔍 Comparing: {p1.title} ↔ {p2.title} | Score = {score}")

            if score > 0.3:  # Lowered threshold
                rel_type = infer_relationship_type(p1, p2)
                obj, created = PolicyRelationship.objects.get_or_create(
                    parent_policy=p1,
                    child_policy=p2,
                    relationship_type=rel_type,
                    defaults={
                        'similarity_score': score,
                        'inferred_from': 'fuzzy_title + tags + tools'
                    }
                )
                if created:
                    print(f"✅ Relationship created: {p1.title} → {p2.title} [{rel_type}, Score={score}]")
                    created_count += 1

    print(f"\n🎯 Total relationships created: {created_count}")

