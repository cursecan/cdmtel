# Generated by Django 2.2 on 2019-05-07 03:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('masterdata', '0018_auto_20190413_1442'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='unlock',
            field=models.BooleanField(default=False),
        ),
    ]