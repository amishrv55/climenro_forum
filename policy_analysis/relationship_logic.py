from rapidfuzz import fuzz
from policy_analysis.models import Policy, PolicyRelationship


#def compute_similarity_score(p1, p2):
 #   score = 0
 #   if p1.country == p2.country:
  #      score += 0.2

 #   score += fuzz.token_sort_ratio(p1.title, p2.title) / 100 * 0.4

 #   common_tools = set(p1.policy_tools or []).intersection(set(p2.policy_tools or []))
  #  score += len(common_tools) / max(len(p1.policy_tools or []), 1) * 0.2

  #  common_tags = set(p1.intent_tags or []).intersection(set(p2.intent_tags or []))
   # score += len(common_tags) / max(len(p1.intent_tags or []), 1) * 0.2

   # return round(score, 2)


def compute_similarity_score(p1, p2):
    score = 0

    if (p1.country or "").strip().lower() == (p2.country or "").strip().lower():
        score += 0.2
    else:
        return 0  # Don't compute similarity across countries

    score += fuzz.token_sort_ratio(p1.title, p2.title) / 100 * 0.4

    common_tools = set(p1.policy_tools or []).intersection(set(p2.policy_tools or []))
    score += len(common_tools) / max(len(p1.policy_tools or []), 1) * 0.2

    common_tags = set(p1.intent_tags or []).intersection(set(p2.intent_tags or []))
    score += len(common_tags) / max(len(p1.intent_tags or []), 1) * 0.2

    return round(score, 2)


def infer_relationship_type(parent, child):
    if child.date_of_issuance and parent.date_of_issuance:
        if child.date_of_issuance > parent.date_of_issuance:
            return 'revision_of'
    return 'related_to'


def create_relationships_for_new_policy(new_policy):
    existing = Policy.objects.exclude(id=new_policy.id)
    for p in existing:
        score = compute_similarity_score(p, new_policy)
        if score > 0.6:
            rel_type = infer_relationship_type(p, new_policy)
            PolicyRelationship.objects.get_or_create(
                parent_policy=p,
                child_policy=new_policy,
                relationship_type=rel_type,
                defaults={
                    'similarity_score': score,
                    'inferred_from': 'upload_metadata_view'
                }
            )


def build_relationships():
    policies = list(Policy.objects.all())
    print(f"Found {len(policies)} policies.")

    for i, p1 in enumerate(policies):
        for j, p2 in enumerate(policies):
            if i == j:
                continue

            score = compute_similarity_score(p1, p2)
            print(f"Comparing '{p1.title}' ↔ '{p2.title}' → Score: {score}")

            if score >= 0.4:  # Threshold
                rel_type = infer_relationship_type(p1, p2)
                obj, created = PolicyRelationship.objects.get_or_create(
                    parent_policy=p1,
                    child_policy=p2,
                    relationship_type=rel_type,
                    defaults={
                        'similarity_score': score,
                        'inferred_from': 'build_relationships()'
                    }
                )
                if created:
                    print(f"✅ Created: {p1.title} → {p2.title} [{rel_type}, {score}]")
