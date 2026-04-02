from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'sensors', views.SensorViewSet)
router.register(r'water-deposits', views.WaterDepositViewSet)
router.register(r'telemetry', views.TelemetryViewSet)
router.register(r'alerts', views.AlertViewSet)

urlpatterns = [
    # Dashboard HTML Pages & HTMX Frags
    path('', views.index, name='dashboard_index'),
    path('htmx/water-deposits/registry/', views.water_deposit_registry, name='water_deposit_registry'),
    path('htmx/water-deposits/critical_feed/', views.critical_deposits_feed, name='critical_deposits_feed'),
    path('htmx/water-deposits/<int:deposit_id>/details/', views.deposit_details, name='deposit_details'),
    path('htmx/ai-chat/', views.ai_chat, name='ai_chat'),
    
    # REST API
    path('api/', include(router.urls)),
]
