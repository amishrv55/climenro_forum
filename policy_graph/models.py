from django.db import models

class PolicyNode(models.Model):
    policy_node = models.CharField(max_length=200)
    policy_title = models.CharField(max_length=300)
    country = models.CharField(max_length=100)
    date = models.DateField()
    graph_intent = models.CharField(max_length=200)
    sector = models.CharField(max_length=100)
    co2_impact = models.FloatField()
    alignment = models.CharField(max_length=50)
    instrument = models.CharField(max_length=100)
    start_end = models.CharField(max_length=100)
    beneficiary = models.CharField(max_length=200)
    influencer = models.CharField(max_length=200)
    efficiency = models.FloatField()
    node_size = models.FloatField()
    node_color = models.CharField(max_length=30)
    original_text = models.TextField()

    def __str__(self):
        return f"{self.policy_title} ({self.country})"
