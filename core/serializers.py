from rest_framework import serializers
from .models import Sensor, WaterDeposit, Hydrometry, Alert

class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        fields = '__all__'

class WaterDepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaterDeposit
        fields = '__all__'

class HydrometrySerializer(serializers.ModelSerializer):
    sensor_name = serializers.CharField(source='sensor.name', read_only=True)

    class Meta:
        model = Hydrometry
        fields = [
            'id', 'sensor', 'sensor_name', 'timestamp', 
            'flow_rate', 'water_level', 'ph_level', 'turbidity'
        ]

class AlertSerializer(serializers.ModelSerializer):
    sensor_name = serializers.CharField(source='sensor.name', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)

    class Meta:
        model = Alert
        fields = [
            'id', 'sensor', 'sensor_name', 'alert_type', 
            'severity', 'severity_display', 'message', 
            'timestamp', 'is_resolved'
        ]
