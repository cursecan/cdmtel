# Generated by Django 2.2 on 2019-08-27 03:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('masterdata', '0020_auto_20190626_1003'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='publish',
            field=models.BooleanField(default=True),
        ),
    ]