# Generated by Django 2.1.5 on 2019-03-20 03:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('masterdata', '0011_customer_no_valid'),
        ('userprofile', '0002_profile_telegram_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='fbcc',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='masterdata.FbccSegment'),
        ),
    ]
