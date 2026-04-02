from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from core.models import WaterDeposit, Alert
from .translations import get_translations

def index(request):
    """
    Main dashboard view. 
    Renders the layout with the Leaflet map and Sidebar.
    """
    lang_code = request.GET.get('lang', 'uz')
    return render(request, 'dashboard/index.html', {
        'current_lang': lang_code,
        't': get_translations(lang_code)
    })

def water_deposit_registry(request):
    """
    HTMX component: Returns a list of all water deposits.
    """
    lang_code = request.GET.get('lang', 'uz')
    deposits = WaterDeposit.objects.all().order_by('name')
    return render(request, 'dashboard/deposit_registry.html', {
        'deposits': deposits,
        'current_lang': lang_code,
        't': get_translations(lang_code)
    })

def critical_deposits_feed(request):
    """
    HTMX feed: Returns critical water deposits.
    """
    lang_code = request.GET.get('lang', 'uz')
    # Filter for critical status as requested
    critical_items = WaterDeposit.objects.filter(status='critical').order_by('name')
    return render(request, 'dashboard/critical_feed.html', {
        'alerts': critical_items,
        'current_lang': lang_code,
        't': get_translations(lang_code)
    })

def deposit_details(request, deposit_id):
    """
    HTMX modal content: Returns specific deposit data.
    """
    lang_code = request.GET.get('lang', 'uz')
    deposit = get_object_or_404(WaterDeposit, id=deposit_id)
    return render(request, 'dashboard/deposit_details.html', {
        'deposit': deposit,
        'current_lang': lang_code,
        't': get_translations(lang_code)
    })

def ai_chat(request):
    """
    HTMX endpoint — AquaAI aqlli chatbot javoblari.
    Real DB ma'lumotlari asosida ishlaydi.
    """
    from .chatbot_engine import process_chat_message
    lang_code = request.GET.get('lang', 'uz')
    user_message = request.POST.get('message', '').strip()
    response_text = process_chat_message(user_message, lang_code)
    return render(request, 'dashboard/ai_message.html', {'response': response_text})
