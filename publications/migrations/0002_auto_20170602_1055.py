# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-02 15:55
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("publications", "0001_initial")]

    operations = [
        migrations.AlterField(
            model_name="publication",
            name="Type",
            field=models.ForeignKey(
                help_text="Begin by selecting the type of publication",
                on_delete=django.db.models.deletion.PROTECT,
                to="publications.Entry_Type",
            ),
        )
    ]