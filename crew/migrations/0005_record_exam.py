# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-07-10 07:53
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('crew', '0004_auto_20160710_1550'),
    ]

    operations = [
        migrations.AddField(
            model_name='record',
            name='exam',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='crew.Exam', verbose_name='考试'),
            preserve_default=False,
        ),
    ]
