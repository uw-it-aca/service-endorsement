# Generated by Django 3.2.21 on 2023-09-13 21:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('endorsement', '0023_auto_20230913_1433'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='accessrecord',
            name='right_id',
        ),
        migrations.RemoveField(
            model_name='accessrecord',
            name='right_name',
        ),
    ]
