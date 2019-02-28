# Generated by Django 2.1.5 on 2019-02-26 05:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('masterdata', '0003_auto_20190127_2010'),
    ]

    operations = [
        migrations.CreateModel(
            name='Segment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('update', models.DateTimeField(auto_now=True)),
                ('segment', models.CharField(max_length=10, unique=True)),
            ],
            options={
                'ordering': ['segment'],
            },
        ),
        migrations.AddField(
            model_name='customer',
            name='bp',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='customer',
            name='customer_name',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='customer',
            name='segment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='masterdata.Segment'),
        ),
    ]