# Generated by Django 2.2 on 2019-07-11 05:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eros', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dadosperfil',
            name='dote',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]