from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SensorViewSet, TelemetryViewSet, AlertViewSet, alert_feed, WaterDepositViewSet

router = DefaultRouter()
router.register(r'sensors', SensorViewSet)
router.register(r'water-deposits', WaterDepositViewSet)
router.register(r'telemetry', TelemetryViewSet)
router.register(r'alerts', AlertViewSet)

urlpatterns = [
    path('alerts/feed/', alert_feed, name='alert_feed'),
    path('', include(router.urls)),
]
