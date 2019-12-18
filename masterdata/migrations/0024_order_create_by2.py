# Generated by Django 2.2 on 2019-12-18 09:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('masterdata', '0023_lockcircuit'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='create_by2',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='orderes', to=settings.AUTH_USER_MODEL),
        ),
    ]
