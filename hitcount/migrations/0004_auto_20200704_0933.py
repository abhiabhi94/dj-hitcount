# Generated by Django 2.0.3 on 2020-07-04 09:33
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ('hitcount', '0003_auto_20190608_1004'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hitcount',
            name='object_pk',
            field=models.PositiveIntegerField(verbose_name='object ID'),
        ),
    ]
