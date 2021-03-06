# Generated by Django 2.1.5 on 2019-01-27 03:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('masterdata', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Avident',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', models.FileField(max_length=200, upload_to='file/avident/')),
            ],
        ),
        migrations.CreateModel(
            name='PermintaanResume',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('update', models.DateTimeField(auto_now=True)),
                ('pic', models.CharField(max_length=15)),
                ('message', models.TextField(blank=True, max_length=500)),
                ('validate', models.BooleanField(default=False)),
                ('executor', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('resume', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='resume_order', to='masterdata.Order')),
                ('sid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='masterdata.Circuit')),
                ('suspend', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='suspend_order', to='masterdata.Order')),
            ],
            options={
                'ordering': ['update', 'timestamp'],
            },
        ),
        migrations.CreateModel(
            name='UpdatePermintaan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('update', models.DateTimeField(auto_now=True)),
                ('message', models.TextField(blank=True, max_length=500)),
                ('permintaan_resume', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cdmsoro.PermintaanResume')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Validation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('update', models.DateTimeField(auto_now=True)),
                ('message', models.TextField(max_length=500)),
                ('action', models.CharField(choices=[('APP', 'APPROVED'), ('DEC', 'REJECTED')], default='DEC', max_length=3)),
                ('permintaan_resume', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cdmsoro.PermintaanResume')),
                ('user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='avident',
            name='leader',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cdmsoro.PermintaanResume'),
        ),
    ]
