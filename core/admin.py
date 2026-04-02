from django.contrib import admin
from .models import Sensor, WaterDeposit, Hydrometry, Alert

@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ('uid', 'name', 'status', 'is_active', 'last_update')
    search_fields = ('uid', 'name')
    list_filter = ('status', 'is_active')

@admin.register(WaterDeposit)
class WaterDepositAdmin(admin.ModelAdmin):
    list_display = ('name', 'deposit_type', 'status', 'latitude', 'longitude')
    search_fields = ('name', 'name_ru', 'name_en')
    list_filter = ('deposit_type', 'status')

@admin.register(Hydrometry)
class HydrometryAdmin(admin.ModelAdmin):
    list_display = ('sensor', 'timestamp', 'flow_rate', 'water_level')
    list_filter = ('sensor', 'timestamp')

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('sensor', 'alert_type', 'severity', 'timestamp', 'is_resolved')
    list_filter = ('severity', 'is_resolved', 'timestamp')
    search_fields = ('message',)
