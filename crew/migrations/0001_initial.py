# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-07-05 18:21
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10)),
                ('grade', models.IntegerField(choices=[(1, '高一'), (3, '高二'), (3, '高三'), (-1, '初一'), (-2, '初二'), (-3, '初三')])),
                ('dept', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crew.Department')),
            ],
        ),
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('staff_id', models.IntegerField()),
                ('name', models.CharField(max_length=6)),
                ('gender', models.CharField(choices=[('M', '男'), ('F', '女')], max_length=1)),
                ('ethnicity', models.CharField(max_length=10)),
                ('native_place', models.CharField(blank=True, max_length=30)),
                ('political_status', models.CharField(choices=[('DY', '中共党员'), ('TY', '共青团员'), ('QZ', '群众')], max_length=2)),
                ('enroll_time', models.DateTimeField()),
                ('degree', models.CharField(max_length=4)),
                ('grad_school', models.CharField(max_length=20)),
                ('major', models.CharField(max_length=10)),
                ('married', models.CharField(choices=[('Y', '已婚'), ('N', '未婚'), ('U', '未知')], max_length=1)),
                ('phone', models.CharField(max_length=15, validators=[django.core.validators.RegexValidator('[\\d|-]+', message='号码格式错误')])),
                ('teaching_level', models.CharField(blank=True, max_length=5)),
                ('teaching', models.CharField(max_length=10)),
                ('admin_level', models.CharField(blank=True, max_length=5)),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='crew.Department')),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_id', models.CharField(max_length=7, unique=True)),
                ('exam_id', models.CharField(blank=True, max_length=10, unique=True, validators=[django.core.validators.RegexValidator('\\d{10}', '考号必须为10位数字')])),
                ('exam_id_alt', models.CharField(blank=True, max_length=10, unique=True, validators=[django.core.validators.RegexValidator('\\d{10}', '考号必须为10位数字')])),
                ('national_id', models.CharField(max_length=18, unique=True)),
                ('name', models.CharField(max_length=6)),
                ('gender', models.CharField(choices=[('M', '男'), ('F', '女')], max_length=1)),
                ('birth_date', models.DateField()),
                ('ethnicity', models.CharField(max_length=10)),
                ('native_place', models.CharField(max_length=30)),
                ('political_status', models.CharField(choices=[('DY', '中共党员'), ('TY', '共青团员'), ('QZ', '群众')], max_length=2)),
                ('hukou_is_agri', models.BooleanField(choices=[(0, '非农业户口'), (1, '农业户口')])),
                ('school', models.CharField(choices=[('BB', '博白'), ('BX', '博学')], max_length=2)),
                ('prop', models.CharField(choices=[('Y', '应届生'), ('W', '往届生')], max_length=1)),
                ('grade_idx', models.SmallIntegerField(choices=[(1, '高一'), (3, '高二'), (3, '高三'), (-1, '初一'), (-2, '初二'), (-3, '初三')])),
                ('class_idx', models.SmallIntegerField()),
                ('category', models.CharField(choices=[('W', '文科'), ('L', '理科'), ('U', '未分科')], max_length=1)),
                ('address', models.CharField(max_length=50)),
                ('phone', models.CharField(max_length=15, validators=[django.core.validators.RegexValidator('[\\d|-]+', message='号码格式错误')])),
                ('enroll_year', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10)),
            ],
        ),
    ]
