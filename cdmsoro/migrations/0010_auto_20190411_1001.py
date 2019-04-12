# Generated by Django 2.1.5 on 2019-04-11 03:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cdmsoro', '0009_permintaanresume_status'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='updatepermintaan',
            options={'ordering': ['timestamp']},
        ),
        migrations.AlterField(
            model_name='updatepermintaan',
            name='permintaan_resume',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='update_permin_bukis', to='cdmsoro.PermintaanResume'),
        ),
    ]