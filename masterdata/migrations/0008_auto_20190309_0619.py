# Generated by Django 2.1.5 on 2019-03-08 23:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('masterdata', '0007_customer_cur_saldo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='segment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='customer_list', to='masterdata.Segment'),
        ),
    ]