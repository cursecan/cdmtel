# Generated by Django 2.1.5 on 2019-03-27 09:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('masterdata', '0012_customer_last_update'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='has_approve',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='customer',
            name='has_validate',
            field=models.BooleanField(default=False),
        ),
    ]