# Generated by Django 2.2 on 2019-06-26 03:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('masterdata', '0019_customer_unlock'),
    ]

    operations = [
        migrations.CreateModel(
            name='CancelOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_num', models.CharField(max_length=20)),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='is_cancel',
            field=models.BooleanField(default=False),
        ),
    ]
