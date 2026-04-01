from django.contrib import admin
from .models import Hydrometry

@admin.register(Hydrometry)
class HydrometryAdmin(admin.ModelAdmin):
    list_display = ('sensor', 'timestamp', 'flow_rate', 'water_level', 'ph_level', 'turbidity')
    list_filter = ('sensor', 'timestamp')
    date_hierarchy = 'timestamp'
    readonly_fields = ('sensor', 'timestamp', 'flow_rate', 'water_level', 'ph_level', 'turbidity')
    ordering = ('-timestamp',)
