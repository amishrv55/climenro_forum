# Generated by Django 5.2.3 on 2025-06-27 11:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='NewsArticle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('cover_image', models.ImageField(blank=True, null=True, upload_to='news_covers/')),
                ('content', models.TextField()),
                ('country', models.CharField(choices=[('India', 'India'), ('USA', 'USA'), ('Canada', 'Canada')], max_length=100)),
                ('sector', models.CharField(choices=[('Energy', 'Energy'), ('Transport', 'Transport'), ('Agriculture', 'Agriculture'), ('Industry', 'Industry'), ('Forestry', 'Forestry'), ('Water', 'Water'), ('Other', 'Other')], max_length=100)),
                ('impact', models.CharField(choices=[('High', 'High'), ('Medium', 'Medium'), ('Low', 'Low')], max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('posted_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
