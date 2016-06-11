# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-11 00:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Endorsee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('netid', models.SlugField(max_length=32, unique=True)),
                ('regid', models.CharField(db_index=True, max_length=32, unique=True)),
                ('display_name', models.CharField(max_length=64, null=True)),
                ('kerberos_active_permitted', models.BooleanField()),
            ],
            options={
                'db_table': 'uw_service_endorsement_endorsee',
            },
        ),
        migrations.CreateModel(
            name='Endorser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('netid', models.SlugField(max_length=32, unique=True)),
                ('regid', models.CharField(db_index=True, max_length=32, unique=True)),
                ('is_valid', models.BooleanField()),
                ('last_visit', models.DateTimeField()),
            ],
            options={
                'db_table': 'uw_service_endorsement_endorser',
            },
        ),
    ]
