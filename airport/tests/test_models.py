from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from airport.models import (
    Crew,
    Airport,
    Route,
    AirplaneType,
    Airplane,
    Flight,
    Order,
    Ticket,
)


class ModelsTests(TestCase):
    def setUp(self) -> None:
        self.crew = Crew.objects.create(
            first_name="John",
            last_name="Hard",
        )
        self.airport1 = Airport.objects.create(
            name="Airport1",
            closest_big_city="City1",
        )
        self.airport2 = Airport.objects.create(
            name="Airport2",
            closest_big_city="City2",
        )
        self.route = Route.objects.create(
            source=self.airport1, destination=self.airport2, distance=100
        )
        self.airplane_type = AirplaneType.objects.create(name="AirplaneType")
        self.airplane = Airplane.objects.create(
            name="Airplane",
            rows=10,
            seats_in_row=6,
            airplane_type=self.airplane_type,
        )
        self.flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time=timezone.now(),
            arrival_time=timezone.now() + timedelta(hours=2),
        )
        self.user = get_user_model().objects.create_user(
            email="test@test.com", password="password"
        )
        self.order = Order.objects.create(user=self.user)

        self.ticket = Ticket(
            row=1,
            seat=1,
            flight=self.flight,
            order=self.order,
        )

    def test_crew_full_name_and_str(self):
        self.assertEqual(
            self.crew.full_name, f"{self.crew.first_name} {self.crew.last_name}"
        )
        self.assertEqual(
            str(self.crew), f"{self.crew.first_name} {self.crew.last_name}"
        )

    def test_airport_str(self):
        self.assertEqual(str(self.airport1), f"{self.airport1.name}")

    def test_route_clean_same_source_and_destination(self):
        route_test = Route(
            source=self.airport1, destination=self.airport1, distance=100
        )
        with self.assertRaises(ValidationError):
            route_test.clean()

    def test_route_clean_different_source_and_destination(self):
        try:
            self.route.clean()
        except ValidationError:
            self.fail("clean() raised ValidationError unexpectedly!")

    def test_route_str(self):
        self.assertEqual(
            str(self.route), f"{self.route.source} -> {self.route.destination}"
        )

    def test_airplane_type_str(self):
        self.assertEqual(str(self.airplane_type), f"{self.airplane_type.name}")

    def test_airplane_capacity_and_str(self):
        self.assertEqual(
            self.airplane.capacity,
            (self.airplane.rows * self.airplane.seats_in_row),
        )
        self.assertEqual(str(self.airplane), f"{self.airplane.name}")

    def test_flight_str(self):
        self.assertEqual(
            str(self.flight),
            f"Flight {self.flight.route} on {self.flight.airplane}",
        )

    def test_order_str(self):
        self.assertEqual(str(self.order), f"{self.order.created_at}")

    def test_validate_ticket_valid_data_and_str(self):
        try:
            self.ticket.save()
        except ValidationError:
            self.fail("validate_ticket raised ValidationError unexpectedly!")

        self.assertEqual(
            str(self.ticket),
            f"{str(self.flight)} (row: {self.ticket.row}, seat: {self.ticket.seat})",
        )

    def test_validate_ticket_invalid_row(self):
        with self.assertRaises(ValidationError):
            Ticket.validate_ticket(
                row=11,
                seat=1,
                flight=self.airplane,
                error_to_raise=ValidationError,
            )

    def test_validate_ticket_invalid_seat(self):
        with self.assertRaises(ValidationError):
            Ticket.validate_ticket(
                row=1,
                seat=7,
                flight=self.airplane,
                error_to_raise=ValidationError,
            )
