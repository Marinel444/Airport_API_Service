# Generated by Django 5.0.3 on 2024-03-12 17:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("airport", "0002_alter_route_options_flight_crews_and_more"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="route",
            unique_together={("source", "destination", "distance")},
        ),
    ]
