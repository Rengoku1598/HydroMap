from celery import shared_task
from sensors.models import Sensor
from .engine import analyze_sensor_flow

@shared_task
def run_flow_balance_analytics():
    """
    Periodic task for Celery Beat: runs flow balance checks for all active sensors.
    """
    active_sensors = Sensor.objects.filter(is_active=True)
    for sensor in active_sensors:
        analyze_sensor_flow(sensor)
