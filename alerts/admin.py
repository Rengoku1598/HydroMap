from django.contrib import admin
from .models import Alert

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('severity', 'alert_type', 'sensor', 'timestamp', 'is_resolved')
    list_filter = ('severity', 'is_resolved', 'sensor')
    search_fields = ('message', 'alert_type')
    readonly_fields = ('sensor', 'alert_type', 'severity', 'message', 'timestamp')
    ordering = ('-timestamp',)
    actions = ['mark_as_resolved']

    def mark_as_resolved(self, request, queryset):
        queryset.update(is_resolved=True)
    mark_as_resolved.short_description = "Отметить как решенные"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('sensor')
