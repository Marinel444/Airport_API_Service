# Generated by Django 5.0.3 on 2024-03-13 19:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("airport", "0004_rename_seats_in_rows_airplane_seats_in_row"),
    ]

    operations = [
        migrations.AlterField(
            model_name="airport",
            name="closest_big_city",
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name="ticket",
            name="order",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="tickets",
                to="airport.order",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="ticket",
            unique_together={("flight", "row", "seat")},
        ),
    ]