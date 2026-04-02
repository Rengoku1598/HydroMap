from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('registry/', views.water_deposit_registry, name='registry'),
    path('critical-feed/', views.critical_deposits_feed, name='critical_feed'),
    path('details/<int:deposit_id>/', views.deposit_details, name='details'),
    path('ai-chat/', views.ai_chat, name='ai_chat'),
]
