# Generated by Django 2.1.5 on 2019-02-28 02:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='coltarget',
            options={'ordering': ['due_date']},
        ),
    ]