# Generated by Django 5.1.3 on 2025-01-24 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user_details',
            name='fullname',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
