# Generated by Django 3.2.9 on 2021-12-03 19:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('uploads', '0016_auto_20211123_1733'),
    ]

    operations = [
        migrations.AlterField(
            model_name='upload',
            name='title',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
