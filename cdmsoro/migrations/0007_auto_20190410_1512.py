# Generated by Django 2.1.5 on 2019-04-10 08:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cdmsoro', '0006_auto_20190409_2009'),
    ]

    operations = [
        migrations.AddField(
            model_name='validation',
            name='closed',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='validation',
            name='message',
            field=models.TextField(blank=True, max_length=500),
        ),
    ]
