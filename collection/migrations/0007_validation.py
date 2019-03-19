# Generated by Django 2.1.5 on 2019-03-19 03:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('masterdata', '0010_auto_20190318_1707'),
        ('collection', '0006_colsegment'),
    ]

    operations = [
        migrations.CreateModel(
            name='Validation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('update', models.DateTimeField(auto_now=True)),
                ('validate', models.CharField(choices=[('RE', 'REJECT'), ('AP', 'APPROVE')], max_length=2)),
                ('msg', models.TextField(max_length=500)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bjt_cust_validate', to='masterdata.Customer')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
