from django import template
from core.models import Sensor, WaterDeposit, Alert

register = template.Library()

@register.simple_tag
def get_sensor_stats():
    return {
        'total': Sensor.objects.count(),
        'active': Sensor.objects.filter(status='active').count(),
        'warning': Sensor.objects.filter(status='warning').count(),
    }

@register.simple_tag
def get_deposit_summary():
    return {
        'total': WaterDeposit.objects.count(),
        'critical': WaterDeposit.objects.filter(status='critical').count(),
    }

@register.inclusion_tag('admin/analytics_widgets.html')
def render_admin_analytics():
    return {
        'sensors': get_sensor_stats(),
        'deposits': get_deposit_summary(),
        'recent_alerts': Alert.objects.all().order_by('-timestamp')[:5]
    }
