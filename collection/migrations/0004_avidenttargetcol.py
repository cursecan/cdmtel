# Generated by Django 2.1.5 on 2019-03-04 02:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('masterdata', '0004_auto_20190226_1205'),
        ('collection', '0003_saldo'),
    ]

    operations = [
        migrations.CreateModel(
            name='AvidenttargetCol',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('update', models.DateTimeField(auto_now=True)),
                ('doc', models.FileField(max_length=200, upload_to='collection/file/')),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='avident_col', to='masterdata.Customer')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
