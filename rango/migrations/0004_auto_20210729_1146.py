# Generated by Django 2.1.5 on 2021-07-29 10:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rango', '0003_page_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='url',
            field=models.URLField(),
        ),
    ]
