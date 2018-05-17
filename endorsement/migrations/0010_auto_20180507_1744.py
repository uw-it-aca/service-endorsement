# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-05-07 17:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('endorsement', '0009_endorser_display_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='endorsementrecord',
            name='acted_as',
            field=models.SlugField(max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name='endorsementrecord',
            name='category_code',
            field=models.SmallIntegerField(choices=[(235, b'UW Office 365'), (234, b'UW G Suite')]),
        ),
    ]