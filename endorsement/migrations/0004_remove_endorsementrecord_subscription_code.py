# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-03-06 23:11
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('endorsement', '0003_auto_20180305_2053'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='endorsementrecord',
            name='subscription_code',
        ),
    ]
