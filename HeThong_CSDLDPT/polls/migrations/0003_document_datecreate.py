# Generated by Django 4.0.2 on 2022-04-30 07:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0002_alter_document_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='datecreate',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
