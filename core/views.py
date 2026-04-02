from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import viewsets
from .models import Sensor, WaterDeposit, Hydrometry, Alert
from .serializers import SensorSerializer, WaterDepositSerializer, HydrometrySerializer, AlertSerializer
from .translations import get_translations

# --- Dashboard Home & HTMX Feeds ---

def index(request):
    lang_code = request.GET.get('lang', 'uz')
    return render(request, 'dashboard/index.html', {
        'current_lang': lang_code,
        't': get_translations(lang_code)
    })

def water_deposit_registry(request):
    lang_code = request.GET.get('lang', 'uz')
    deposits = WaterDeposit.objects.all().order_by('name')
    return render(request, 'dashboard/deposit_registry.html', {
        'deposits': deposits,
        'current_lang': lang_code,
        't': get_translations(lang_code)
    })

def critical_deposits_feed(request):
    lang_code = request.GET.get('lang', 'uz')
    # Filter for critical status as seen in the screenshots
    deposits = WaterDeposit.objects.filter(status='critical').order_by('name')
    # If no critical, return empty indicator
    return render(request, 'dashboard/critical_feed.html', {
        'deposits': deposits,
        'current_lang': lang_code,
        't': get_translations(lang_code)
    })

def deposit_details(request, deposit_id):
    lang_code = request.GET.get('lang', 'uz')
    try:
        deposit = WaterDeposit.objects.get(id=deposit_id)
        return render(request, 'dashboard/deposit_details.html', {
            'deposit': deposit,
            'current_lang': lang_code,
            't': get_translations(lang_code)
        })
    except WaterDeposit.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)

# --- AI Chat Engine ---

def ai_chat(request):
    lang_code = request.GET.get('lang', 'uz')
    user_message = request.POST.get('message', '')
    
    # Minimal mock AI logic locally for now (Gemini integration would go here)
    t = get_translations(lang_code)
    response_text = f"O'zbekiston hududiy suv nazorati tizimi. {user_message} - bu bo'yicha ma'lumotlar tahlil qilinmoqda."
    
    if lang_code == 'ru':
        response_text = f"Система регионального водного мониторинга Узбекистана. Анализируем ваш запрос: {user_message}."
    elif lang_code == 'en':
        response_text = f"Uzbekistan National Water Monitoring System. Analyzing your request: {user_message}."
        
    return render(request, 'dashboard/ai_message.html', {'response': response_text})

# --- REST ViewSets for Map & API ---

class SensorViewSet(viewsets.ModelViewSet):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer

class WaterDepositViewSet(viewsets.ModelViewSet):
    queryset = WaterDeposit.objects.all()
    serializer_class = WaterDepositSerializer

class TelemetryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Hydrometry.objects.all().select_related('sensor')
    serializer_class = HydrometrySerializer

class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.all().select_related('sensor')
    serializer_class = AlertSerializer
