from rest_framework import serializers
from .models import Alert

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
