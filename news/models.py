from django.db import models
from django.contrib.auth.models import User
from PIL import Image
import os

# Create your models here.

class NewsArticle(models.Model):
    IMPACT_CHOICES = [
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
    ]

    SECTOR_CHOICES = [
        ('Energy', 'Energy'),
        ('Transport', 'Transport'),
        ('Agriculture', 'Agriculture'),
        ('Industry', 'Industry'),
        ('Forestry', 'Forestry'),
        ('Water', 'Water'),
        ('Other', 'Other'),
    ]

    COUNTRY_CHOICES = [
        ('India', 'India'),
        ('USA', 'USA'),
        ('Canada', 'Canada'),
        # Add more as needed
    ]

    title = models.CharField(max_length=200)
    cover_image = models.ImageField(upload_to='news_covers/', blank=True, null=True)
    content = models.TextField()
    country = models.CharField(max_length=100, choices=COUNTRY_CHOICES)
    sector = models.CharField(max_length=100, choices=SECTOR_CHOICES)
    impact = models.CharField(max_length=10, choices=IMPACT_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.cover_image:
            img_path = self.cover_image.path
            img = Image.open(img_path)

            max_size = (800, 250)
            img = img.resize(max_size, Image.Resampling.LANCZOS)
            img.save(img_path)

    def __str__(self):
        return self.title
