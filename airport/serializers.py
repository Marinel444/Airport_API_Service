from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from airport.models import Crew, Airport, Route, AirplaneType, Airplane, Flight, Order, Ticket


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city")


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = "__all__"


class RouteListSerializer(serializers.ModelSerializer):
    source = serializers.StringRelatedField(read_only=True)
    destination = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = "__all__"


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ("id", "name", "airplane_type", "rows", "seats_in_row")


class AirplaneListSerializer(AirplaneSerializer):
    airplane_type = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Airplane
        fields = ("id", "name", "airplane_type", "capacity")


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "departure_time", "arrival_time", "crews")


class FlightListSerializer(FlightSerializer):
    route = serializers.StringRelatedField(read_only=True)
    airplane = serializers.CharField(source="airplane.name", read_only=True)
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "departure_time", "arrival_time", "tickets_available")


class TicketSerializer(serializers.ModelSerializer):

    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs=attrs)
        Ticket.validate_ticket(
            attrs["row"],
            attrs["seat"],
            attrs["flight"].airplane,
            ValidationError
        )
        return data

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight")


class TicketListSerializer(TicketSerializer):
    flight = FlightListSerializer(read_only=True)


class TicketSeatsSerializer(TicketSerializer):
    class Meta:
        model = Ticket
        fields = ("row", "seat")


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "tickets", "created_at")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)


class FlightDetailSerializer(FlightSerializer):
    route = RouteListSerializer(read_only=True)
    airplane = AirplaneListSerializer(read_only=True)
    crews = serializers.SlugRelatedField(slug_field="full_name", read_only=True, many=True)
    taken_place = TicketSeatsSerializer(read_only=True, many=True)

    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "crews", "taken_place")
