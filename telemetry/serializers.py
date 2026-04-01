from rest_framework import serializers
from .models import Hydrometry

class HydrometrySerializer(serializers.ModelSerializer):
    sensor_name = serializers.CharField(source='sensor.name', read_only=True)

    class Meta:
        model = Hydrometry
        fields = [
            'id', 'sensor', 'sensor_name', 'timestamp', 
            'flow_rate', 'water_level', 'ph_level', 'turbidity'
        ]
