from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name


class Airport(models.Model):
    name = models.CharField(max_length=255)
    closest_big_city = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Route(models.Model):
    source = models.ForeignKey(Airport, related_name="departures", on_delete=models.CASCADE)
    destination = models.ForeignKey(Airport, related_name="arrivals", on_delete=models.CASCADE)
    distance = models.IntegerField()

    class Meta:
        unique_together = ("source", "destination", "distance")
        ordering = ("distance",)

    def clean(self):
        if self.destination == self.source:
            raise ValidationError("Source and destination names should be difference")

    def save(self, *args, **kwargs):
        self.clean()
        return super(Route, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.source} -> {self.destination}"


class AirplaneType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(AirplaneType, related_name="airplanes", on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row


class Flight(models.Model):
    route = models.ForeignKey(Route, related_name="flights", on_delete=models.CASCADE)
    airplane = models.ForeignKey(Airplane, related_name="flights", on_delete=models.CASCADE)
    crews = models.ManyToManyField(Crew, related_name="flights")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    def __str__(self):
        return f"Flight {self.route} on {self.airplane}"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="user", on_delete=models.CASCADE)

    def __str__(self):
        return str(self.created_at)


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(Flight, related_name="tickets", on_delete=models.CASCADE)
    order = models.ForeignKey(Order, related_name="ticket", on_delete=models.CASCADE)

    def __str__(self):
        return (
            f"{str(self.flight)} (row: {self.row}, seat: {self.seat})"
        )
