from django.contrib import admin
from .models import Sensor

@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ('name', 'uid', 'canal_name', 'status', 'is_active', 'last_update')
    list_filter = ('status', 'is_active', 'canal_name')
    search_fields = ('name', 'uid', 'canal_name')
    ordering = ('canal_name', 'name')
    fieldsets = (
        ('General Info', {
            'fields': ('uid', 'name', 'canal_name', 'status', 'is_active')
        }),
        ('GIS & Topology', {
            'fields': ('latitude', 'longitude', 'upstream_sensor')
        }),
        ('Flow Thresholds', {
            'fields': ('max_flow_rate', 'min_flow_rate')
        }),
    )
