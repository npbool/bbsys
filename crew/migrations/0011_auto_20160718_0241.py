# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-07-17 18:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crew', '0010_grade'),
    ]

    operations = [
        migrations.AddField(
            model_name='subject',
            name='level_a_score',
            field=models.FloatField(default=0, verbose_name='一本分数'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='subject',
            name='level_b_score',
            field=models.FloatField(default=0, verbose_name='二本分数'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='classteacher',
            name='grade_idx',
            field=models.IntegerField(choices=[(1, '高一年级'), (2, '高二年级'), (3, '高三年级'), (-1, '初一年级'), (-2, '初二年级'), (-3, '初三年级')], verbose_name='年级'),
        ),
        migrations.AlterField(
            model_name='grade',
            name='id',
            field=models.IntegerField(choices=[(1, '高一年级'), (2, '高二年级'), (3, '高三年级'), (-1, '初一年级'), (-2, '初二年级'), (-3, '初三年级')], primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='leader',
            name='grade_idx',
            field=models.IntegerField(choices=[(1, '高一年级'), (2, '高二年级'), (3, '高三年级'), (-1, '初一年级'), (-2, '初二年级'), (-3, '初三年级')], verbose_name='年级'),
        ),
        migrations.AlterField(
            model_name='person',
            name='grade',
            field=models.IntegerField(choices=[(1, '高一年级'), (2, '高二年级'), (3, '高三年级'), (-1, '初一年级'), (-2, '初二年级'), (-3, '初三年级')]),
        ),
        migrations.AlterField(
            model_name='student',
            name='grade_idx',
            field=models.SmallIntegerField(choices=[(1, '高一年级'), (2, '高二年级'), (3, '高三年级'), (-1, '初一年级'), (-2, '初二年级'), (-3, '初三年级')], verbose_name='年级'),
        ),
        migrations.AlterField(
            model_name='subjectleader',
            name='grade_idx',
            field=models.IntegerField(choices=[(1, '高一年级'), (2, '高二年级'), (3, '高三年级'), (-1, '初一年级'), (-2, '初二年级'), (-3, '初三年级')], verbose_name='年级'),
        ),
    ]