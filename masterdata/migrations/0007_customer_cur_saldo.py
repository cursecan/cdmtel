# Generated by Django 2.1.5 on 2019-03-04 08:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('masterdata', '0006_customer_has_target'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='cur_saldo',
            field=models.DecimalField(decimal_places=0, default=0, max_digits=12),
        ),
    ]
