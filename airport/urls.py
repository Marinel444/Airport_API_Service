from django.urls import path, include
from rest_framework import routers

from airport.views import (
    CrewViewSet,
    AirportViewSet,
    RouteViewSet,
    AirplaneTypeViewSet,
    AirplaneViewSet,
    FlightViewSet,
    OrderViewSet,
)

router = routers.DefaultRouter()
router.register(r"crews", CrewViewSet, basename="crews")
router.register(r"airports", AirportViewSet, basename="airports")
router.register(r"routes", RouteViewSet, basename="routes")
router.register(r"airplane_types", AirplaneTypeViewSet, basename="airplane_types")
router.register(r"airplanes", AirplaneViewSet, basename="airplanes")
router.register(r"flights", FlightViewSet, basename="flights")
router.register(r"orders", OrderViewSet, basename="orders")


urlpatterns = [
    path("", include(router.urls)),
]

app_name = "airport"
