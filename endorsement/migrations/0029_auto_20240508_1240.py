# Generated by Django 3.2.25 on 2024-05-08 19:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('endorsement', '0028_auto_20240506_1259'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shareddriverecord',
            name='acceptance',
        ),
        migrations.DeleteModel(
            name='SharedDriveAcceptance',
        ),
    ]
