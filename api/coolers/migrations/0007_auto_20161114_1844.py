# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-14 18:44
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('coolers', '0006_auto_20161108_1818'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cooler',
            name='uuid',
            field=models.CharField(default=uuid.uuid4, max_length=100, unique=True),
        ),
    ]