# Generated by Django 2.0.3 on 2019-06-08 10:04
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ('hitcount', '0002_index_ip_and_session'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hitcount',
            name='object_pk',
            field=models.CharField(max_length=128, verbose_name='object ID'),
        ),
    ]
