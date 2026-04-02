from rest_framework import viewsets
from core.models import Sensor, WaterDeposit, Hydrometry, Alert
from core.serializers import SensorSerializer, WaterDepositSerializer, HydrometrySerializer, AlertSerializer
from django.shortcuts import render

class SensorViewSet(viewsets.ModelViewSet):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer

class WaterDepositViewSet(viewsets.ModelViewSet):
    queryset = WaterDeposit.objects.all()
    serializer_class = WaterDepositSerializer

class TelemetryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Hydrometry.objects.all().select_related('sensor')
    serializer_class = HydrometrySerializer

class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.all().select_related('sensor')
    serializer_class = AlertSerializer

def alert_feed(request):
    """
    HTMX endpoint: Returns the recent alerts in HTML fragment form.
    """
    alerts = Alert.objects.all().order_by('-timestamp')[:8]
    return render(request, 'dashboard/alerts_feed.html', {'alerts': alerts})
