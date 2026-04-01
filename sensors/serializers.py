from rest_framework import serializers
from .models import Sensor, WaterDeposit

class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        fields = '__all__'

class WaterDepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaterDeposit
        fields = '__all__'
