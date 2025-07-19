from django.db import models

class Policy(models.Model):
    policy_id = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=255)
    summary = models.TextField(blank=True, null=True)
    year = models.IntegerField()
    date_of_issuance = models.DateField()
    country = models.CharField(max_length=100)
    document_type = models.CharField(max_length=100)
    is_fundamental = models.BooleanField(default=False)
    has_children = models.BooleanField(default=False)
    num_sections = models.IntegerField(default=0)

    # Multi-value fields stored safely as lists
    sectors = models.JSONField(blank=True, null=True)
    sub_sectors = models.JSONField(blank=True, null=True)
    intent_tags = models.JSONField(blank=True, null=True)
    policy_tools = models.JSONField(blank=True, null=True)
    responsible_ministries = models.JSONField(blank=True, null=True)
    linked_documents = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.title


class PolicySection(models.Model):
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name='sections')
    section_id = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=255)
    summary = models.TextField()

    sector = models.CharField(max_length=100, blank=True)
    sub_sectors = models.JSONField(blank=True, null=True)
    intent_tags = models.JSONField(blank=True, null=True)
    policy_type = models.CharField(max_length=100, blank=True)
    policy_tools = models.JSONField(blank=True, null=True)
    responsible_ministries = models.JSONField(blank=True, null=True)
    linked_documents = models.JSONField(blank=True, null=True)

    global_alignment = models.TextField(blank=True, null=True)
    is_legally_binding = models.CharField(max_length=100, blank=True, null=True)
    compliance_type = models.TextField(blank=True, null=True)
    mrv_system = models.TextField(blank=True, null=True)
    monitoring_mechanism = models.TextField(blank=True, null=True)
    targets = models.TextField(blank=True, null=True)
    impact_estimate = models.TextField(blank=True, null=True)
    climate_finance = models.TextField(blank=True, null=True)
    financial_outlay = models.TextField(blank=True, null=True)
    yearly_budget = models.TextField(blank=True, null=True)
    timeline = models.TextField(blank=True, null=True)
    lifecycle_history = models.TextField(blank=True, null=True)
    kpis = models.TextField(blank=True, null=True)
    linked_ndcs_or_sdgs = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.policy.title} - {self.title}"
