# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-01 22:44
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20171128_1517'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment', to='core.Task'),
        ),
    ]