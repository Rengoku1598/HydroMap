from django.db.models import Avg
from django.utils import timezone
from datetime import timedelta
from sensors.models import Sensor
from telemetry.models import Hydrometry
from alerts.models import Alert

def analyze_sensor_flow(sensor: Sensor):
    """
    Algorithm: Flow Balance Differential (FBD)
    Compares latest flow between a sensor and its upstream neighbor.
    If loss exceeds 20%, triggers a 'theft_detected' alert.
    """
    if not sensor.upstream_sensor:
        return
    
    # 1. Get average flow for the last 5 minutes
    now = timezone.now()
    range_start = now - timedelta(minutes=5)
    
    upper_data = Hydrometry.objects.filter(
        sensor=sensor.upstream_sensor,
        timestamp__gte=range_start
    ).aggregate(avg=Avg('flow_rate'))
    
    lower_data = Hydrometry.objects.filter(
        sensor=sensor,
        timestamp__gte=range_start
    ).aggregate(avg=Avg('avg_flow')) # Note: mapping might vary if field name is different
    
    # Using fixed field mapping for reliability
    upper_flow = upper_data.get('avg')
    lower_flow = Hydrometry.objects.filter(
        sensor=sensor,
        timestamp__gte=range_start
    ).aggregate(avg=Avg('flow_rate')).get('avg')

    if upper_flow is not None and lower_flow is not None:
        loss = upper_flow - lower_flow
        threshold = upper_flow * 0.20 # 20% tolerance for evaporation/seepage
        
        if loss > threshold:
            Alert.objects.get_or_create(
                sensor=sensor,
                alert_type='theft_detected',
                severity='critical',
                message=f"CRITICAL: Flow imbalance of {loss:.2f} m3/s detected between {sensor.upstream_sensor.name} and {sensor.name}. Potential illegal water interception."
            )
        elif lower_flow < sensor.min_flow_rate:
            Alert.objects.get_or_create(
                sensor=sensor,
                alert_type='low_flow',
                severity='warning',
                message=f"Warning: Flow rate {lower_flow:.2f} m3/s dropped below minimum threshold for {sensor.name}."
            )
