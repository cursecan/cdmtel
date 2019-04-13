# Generated by Django 2.1.5 on 2019-04-12 04:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('masterdata', '0015_auto_20190410_1047'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(10, None), (1, 'Waiting Validation'), (2, 'Waiting Approval'), (3, 'Rejected'), (4, 'Approved')], default=10),
        ),
    ]