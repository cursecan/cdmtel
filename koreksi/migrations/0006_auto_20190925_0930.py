# Generated by Django 2.2 on 2019-09-25 02:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('koreksi', '0005_inputkoreksi_customer_obj'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inputkoreksi',
            name='wb',
            field=models.CharField(max_length=10, verbose_name='Bandwidth'),
        ),
    ]