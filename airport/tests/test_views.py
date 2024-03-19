from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import F, Count
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import (
    Crew,
    Airport,
    Route,
    AirplaneType,
    Airplane,
    Flight,
    Order,
)
from airport.serializers import (
    CrewSerializer,
    AirportSerializer,
    RouteListSerializer,
    AirplaneTypeSerializer,
    AirplaneSerializer,
    AirplaneListSerializer,
    FlightListSerializer,
    FlightDetailSerializer,
    OrderListSerializer,
)


def get_simple_user(**params):
    default = {"email": "test@test.com", "password": "password"}
    default.update(params)
    return get_user_model().objects.create_user(**default)


def get_airport(**params):
    default = {"name": "test1", "closest_big_city": "city1"}
    default.update(params)
    return Airport.objects.create(**default)


def get_route(**params):
    default = {
        "source": get_airport(),
        "destination": get_airport(name="test2", closest_big_city="city2"),
        "distance": 500,
    }
    default.update(params)
    return Route.objects.create(**default)


def get_airplane_type(**params):
    default = {"name": "type1"}
    default.update(params)
    return AirplaneType.objects.create(**default)


def get_airplane(**params):
    default = {
        "name": "test1",
        "rows": 10,
        "seats_in_row": 6,
        "airplane_type": get_airplane_type(),
    }
    default.update(params)
    return Airplane.objects.create(**default)


class CrewViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.CREW_URL = reverse("airport:crews-list")

    def test_unauthenticated_crew_api(self):
        response = self.client.get(self.CREW_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_crew_api(self):
        user = get_simple_user()
        self.client.force_authenticate(user=user)
        response = self.client.get(self.CREW_URL)
        crews = Crew.objects.all()
        serializer = CrewSerializer(crews, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_create_crew(self):
        super_user = get_simple_user(is_staff=True)
        self.client.force_authenticate(user=super_user)
        result = self.client.post(
            self.CREW_URL, {"first_name": "crew2", "last_name": "crew3"}
        )
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)


class AirportViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.AIRPORT_URL = reverse("airport:airports-list")
        get_airport()

    def test_unauthenticated_airport_api(self):
        response = self.client.get(self.AIRPORT_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_airport_api(self):
        user = get_simple_user()
        self.client.force_authenticate(user=user)
        response = self.client.get(self.AIRPORT_URL)
        airports = Airport.objects.all()
        serializer = AirportSerializer(airports, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_create_airport(self):
        super_user = get_simple_user(is_staff=True)
        self.client.force_authenticate(user=super_user)
        result = self.client.post(
            self.AIRPORT_URL, {"name": "DLM", "closest_big_city": "Dubai"}
        )
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)


class RouteViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.ROUTE_URL = reverse("airport:routes-list")
        self.airport1 = get_airport()
        self.airport2 = get_airport(name="test2", closest_big_city="city2")
        self.route = get_route(source=self.airport1, destination=self.airport2)

    def test_unauthenticated_route_api(self):
        response = self.client.get(self.ROUTE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_route_api(self):
        user = get_simple_user()
        self.client.force_authenticate(user=user)
        response = self.client.get(self.ROUTE_URL)
        routes = Route.objects.all()
        serializer = RouteListSerializer(routes, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_list_route_api_with_filters(self):
        user = get_simple_user()
        self.client.force_authenticate(user=user)
        airport3 = get_airport(name="test3", closest_big_city="city3")
        airport4 = get_airport(name="test4", closest_big_city="city4")
        get_route(source=airport3, destination=airport4, distance=500)
        response = self.client.get(
            self.ROUTE_URL, {"source": "city1", "destination": "city2"}
        )
        serializer = RouteListSerializer(self.route)

        self.assertIn(serializer.data, response.data["results"])

    def test_create_route(self):
        super_user = get_simple_user(is_staff=True)
        self.client.force_authenticate(user=super_user)
        result = self.client.post(
            self.ROUTE_URL,
            {
                "distance": 100,
                "source": self.airport2.id,
                "destination": self.airport1.id,
            },
        )
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)


class AirplaneTypeViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.AIRPLANE_TYPE_URL = reverse("airport:airplane_types-list")
        self.airplane_type = get_airplane_type()

    def test_unauthenticated_airplane_type_api(self):
        response = self.client.get(self.AIRPLANE_TYPE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_airplane_type_api(self):
        user = get_simple_user()
        self.client.force_authenticate(user=user)
        response = self.client.get(self.AIRPLANE_TYPE_URL)
        airplane_types = AirplaneType.objects.all()
        serializer = AirplaneTypeSerializer(airplane_types, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_create_airplane_type(self):
        super_user = get_simple_user(is_staff=True)
        self.client.force_authenticate(user=super_user)
        result = self.client.post(self.AIRPLANE_TYPE_URL, {"name": "type2"})
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)


class AirplaneViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.AIRPLANE_URL = reverse("airport:airplanes-list")
        self.airplane = get_airplane()

    def test_unauthenticated_airplane_api(self):
        response = self.client.get(self.AIRPLANE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_airplane_api(self):
        user = get_simple_user()
        self.client.force_authenticate(user=user)
        response = self.client.get(self.AIRPLANE_URL)
        airplanes = Airplane.objects.all()
        serializer = AirplaneListSerializer(airplanes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_retrieve_airplane_api(self):
        user = get_simple_user()
        self.client.force_authenticate(user=user)
        response = self.client.get(f"{self.AIRPLANE_URL}{self.airplane.id}/")
        serializer = AirplaneSerializer(self.airplane)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_list_airplane_api_with_filters(self):
        user = get_simple_user()
        self.client.force_authenticate(user=user)
        airplane_type1 = get_airplane_type(name="type2")
        airplane2 = get_airplane(name="test2", airplane_type=airplane_type1)
        response = self.client.get(
            self.AIRPLANE_URL, {"airplane_type": "type2"}
        )
        serializer = AirplaneListSerializer(airplane2)

        self.assertIn(serializer.data, response.data["results"])


class FlightViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.FLIGHT_URL = reverse("airport:flights-list")
        self.route = get_route()
        self.airplane = get_airplane()
        self.flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time=timezone.now(),
            arrival_time=timezone.now() + timedelta(hours=2),
        )

    def test_unauthenticated_flight_api(self):
        response = self.client.get(self.FLIGHT_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_flight_api(self):
        user = get_simple_user()
        self.client.force_authenticate(user=user)
        response = self.client.get(self.FLIGHT_URL)
        flights = Flight.objects.annotate(
            tickets_available=(
                F("airplane__rows") * F("airplane__seats_in_row")
                - Count("tickets")
            )
        )
        serializer = FlightListSerializer(flights, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_retrieve_flight_api(self):
        user = get_simple_user()
        self.client.force_authenticate(user=user)
        response = self.client.get(f"{self.FLIGHT_URL}{self.flight.id}/")
        flight1 = Flight.objects.get(id=self.flight.id)
        serializer = FlightDetailSerializer(flight1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_list_airplane_api_with_filters(self):
        user = get_simple_user()
        self.client.force_authenticate(user=user)

        response = self.client.get(
            self.FLIGHT_URL, {"source": "test1", "destination": "test2"}
        )
        flights = Flight.objects.filter(
            route__source__name="test1", route__destination__name="test2"
        ).annotate(
            tickets_available=(
                F("airplane__rows") * F("airplane__seats_in_row")
                - Count("tickets")
            )
        )
        serializer = FlightListSerializer(flights[0])

        self.assertIn(serializer.data, response.data["results"])


class OrderViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.ORDERS_URL = reverse("airport:orders-list")
        self.route = get_route()
        self.airplane = get_airplane()
        self.flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time=timezone.now(),
            arrival_time=timezone.now() + timedelta(hours=2),
        )

    def test_list_and_create_order(self):
        user = get_simple_user()
        self.client.force_authenticate(user=user)
        data = {
            "tickets": [{"row": 1, "seat": 1, "flight": self.flight.id}],
        }
        create = self.client.post(self.ORDERS_URL, data, format="json")
        response = self.client.get(self.ORDERS_URL)
        orders = Order.objects.all()
        serializer = OrderListSerializer(orders, many=True)
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)
        self.assertEqual(serializer.data, response.data["results"])
