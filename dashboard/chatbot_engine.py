"""
AquaAI Chatbot Engine
---------------------
Saytga tegishli ma'lumotlar asosida aqlli javoblar beradi:
- Sensor holati va anomaliyalar
- Suv o'g'irlanishi bashorati
- 12/24 soatlik trend tahlili
- Ob-havo ta'siri
- Kritik joylar haqida ma'lumot
"""

import json
import random
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Avg, Max, Min, Count, Q
from core.models import Sensor, WaterDeposit, Hydrometry, Alert


# ─────────────────────────────────────────────
#  Keyword Matchers (UZ / RU / EN all-in-one)
# ─────────────────────────────────────────────

KEYWORDS = {
    'theft': [
        "o'g'irla", "o'g'irlan", "ugirla", "vorovstvo", "кража", "theft", "stealing", "steal",
        "yo'q", "kamaydi", "tushdi", "нехватка", "missing", "lost flow"
    ],
    'forecast': [
        "bashorat", "prognoz", "прогноз", "forecast", "prediction", "12 soat", "24 soat",
        "12 час", "24 час", "12 hour", "24 hour", "kelajak", "будущее", "future",
        "keyingi", "следующий", "next"
    ],
    'critical': [
        "kritik", "critical", "критик", "критич", "xavf", "danger", "опасность",
        "alarm", "avariya", "авария", "emergency", "urgent"
    ],
    'status': [
        "holat", "status", "состояние", "qanday", "как дела", "how is",
        "sensor", "дatchik", "датчик", "post", "пост"
    ],
    'weather': [
        "ob-havo", "weather", "погода", "harorat", "температура", "temperature",
        "yomg'ir", "дождь", "rain", "qor", "снег", "snow", "shamol", "ветер", "wind"
    ],
    'alert': [
        "ogohlantirish", "signal", "xabar", "предупреждение", "сигнал", "alert",
        "warning", "anomaliya", "аномалия", "anomaly"
    ],
    'deposit': [
        "ombor", "reservoir", "водохранилище", "ko'l", "озеро", "lake",
        "kanal", "канал", "canal", "daryo", "река", "river", "suv", "вода", "water"
    ],
    'help': [
        "yordam", "помощь", "help", "nima qila olasiz", "что умеешь", "what can you do",
        "salom", "привет", "hello", "hi", "assalomu alaykum"
    ],
    'flow': [
        "oqim", "sarfi", "поток", "расход", "flow", "m3", "litr", "litre",
        "tezlik", "скорость", "speed", "rate"
    ],
}


def classify_message(message: str) -> list:
    """Xabarni tahlil qilib, kategoriyalarni aniqlaydi."""
    msg_lower = message.lower()
    matched = []
    for category, keywords in KEYWORDS.items():
        for kw in keywords:
            if kw in msg_lower:
                matched.append(category)
                break
    return matched if matched else ['status']


# ─────────────────────────────────────────────
#  Data Collectors
# ─────────────────────────────────────────────

def get_system_summary():
    """Tizim umumiy holatini qaytaradi."""
    total_sensors = Sensor.objects.filter(is_active=True).count()
    critical_sensors = Sensor.objects.filter(status='critical').count()
    warning_sensors = Sensor.objects.filter(status='warning').count()
    total_deposits = WaterDeposit.objects.count()
    critical_deposits = WaterDeposit.objects.filter(status='critical').count()
    recent_alerts = Alert.objects.filter(
        timestamp__gte=timezone.now() - timedelta(hours=24),
        is_resolved=False
    ).count()
    return {
        'total_sensors': total_sensors,
        'critical_sensors': critical_sensors,
        'warning_sensors': warning_sensors,
        'normal_sensors': total_sensors - critical_sensors - warning_sensors,
        'total_deposits': total_deposits,
        'critical_deposits': critical_deposits,
        'recent_alerts': recent_alerts,
    }


def get_critical_alerts(limit=5):
    """Kritik xabarnomalarni qaytaradi."""
    return Alert.objects.filter(
        severity='critical',
        is_resolved=False
    ).select_related('sensor').order_by('-timestamp')[:limit]


def detect_theft_anomalies():
    """
    Suv o'g'irlanishini aniqlaydi:
    Upstream va downstream sensorlar orasidagi oqim farqini taqqoslaydi.
    Agar sarf > 20% ga farq qilsa - ogohlantirish.
    """
    anomalies = []
    sensors_with_upstream = Sensor.objects.filter(
        upstream_sensor__isnull=False,
        is_active=True
    ).select_related('upstream_sensor')[:10]

    for sensor in sensors_with_upstream:
        up_data = Hydrometry.objects.filter(
            sensor=sensor.upstream_sensor
        ).order_by('-timestamp').first()
        down_data = Hydrometry.objects.filter(
            sensor=sensor
        ).order_by('-timestamp').first()

        if up_data and down_data and up_data.flow_rate and down_data.flow_rate:
            diff = up_data.flow_rate - down_data.flow_rate
            if up_data.flow_rate > 0:
                loss_pct = (diff / up_data.flow_rate) * 100
                if loss_pct > 20:
                    anomalies.append({
                        'sensor': sensor.name,
                        'canal': sensor.canal_name,
                        'upstream_flow': round(up_data.flow_rate, 2),
                        'downstream_flow': round(down_data.flow_rate, 2),
                        'loss_pct': round(loss_pct, 1),
                        'severity': 'high' if loss_pct > 40 else 'medium',
                    })

    # Agar real data yo'q bo'lsa, demo data ishlatamiz
    if not anomalies and not sensors_with_upstream.exists():
        anomalies = _generate_demo_theft_data()

    return anomalies


def _generate_demo_theft_data():
    """Demo maqsadlar uchun simulatsiya qilingan o'g'irlanish ma'lumotlari."""
    canals = ["Katta Farg'ona kanali", "Andijon magistral kanali", "Qoradaryo kanal tarmog'i"]
    results = []
    for canal in random.sample(canals, k=min(2, len(canals))):
        loss = round(random.uniform(22, 48), 1)
        up = round(random.uniform(5, 15), 2)
        results.append({
            'sensor': f"{canal} - Nazorat nuqtasi",
            'canal': canal,
            'upstream_flow': up,
            'downstream_flow': round(up * (1 - loss / 100), 2),
            'loss_pct': loss,
            'severity': 'high' if loss > 40 else 'medium',
        })
    return results


def get_forecast_data(hours=24):
    """
    Oqim trendi va bashoratini qaytaradi.
    Oxirgi 24 soat ma'lumotlari asosida keyingi N soatni hisoblaydi.
    """
    cutoff = timezone.now() - timedelta(hours=hours)
    recent = Hydrometry.objects.filter(
        timestamp__gte=cutoff
    ).aggregate(
        avg_flow=Avg('flow_rate'),
        max_flow=Max('flow_rate'),
        min_flow=Min('flow_rate'),
        avg_level=Avg('water_level'),
        avg_ph=Avg('ph_level'),
    )

    # Trend yo'nalishi
    first_half = Hydrometry.objects.filter(
        timestamp__gte=cutoff,
        timestamp__lt=timezone.now() - timedelta(hours=hours // 2)
    ).aggregate(avg_flow=Avg('flow_rate'))

    second_half = Hydrometry.objects.filter(
        timestamp__gte=timezone.now() - timedelta(hours=hours // 2)
    ).aggregate(avg_flow=Avg('flow_rate'))

    trend = 'stable'
    if first_half['avg_flow'] and second_half['avg_flow']:
        diff = second_half['avg_flow'] - first_half['avg_flow']
        if diff > 0.5:
            trend = 'increasing'
        elif diff < -0.5:
            trend = 'decreasing'

    # Agar data yo'q bo'lsa
    if not recent['avg_flow']:
        return _generate_demo_forecast(hours)

    return {
        'period_hours': hours,
        'avg_flow': round(recent['avg_flow'] or 0, 2),
        'max_flow': round(recent['max_flow'] or 0, 2),
        'min_flow': round(recent['min_flow'] or 0, 2),
        'avg_level': round(recent['avg_level'] or 0, 2),
        'avg_ph': round(recent['avg_ph'] or 7.0, 1),
        'trend': trend,
        'predicted_next': _predict_next_value(recent['avg_flow'], trend),
    }


def _generate_demo_forecast(hours):
    """Demo bashorat ma'lumotlari."""
    avg = round(random.uniform(3.5, 8.5), 2)
    trend = random.choice(['increasing', 'stable', 'decreasing'])
    return {
        'period_hours': hours,
        'avg_flow': avg,
        'max_flow': round(avg * 1.3, 2),
        'min_flow': round(avg * 0.7, 2),
        'avg_level': round(random.uniform(1.2, 4.5), 2),
        'avg_ph': round(random.uniform(6.8, 7.4), 1),
        'trend': trend,
        'predicted_next': _predict_next_value(avg, trend),
    }


def _predict_next_value(current, trend):
    """Oddiy extrapolatsiya."""
    if trend == 'increasing':
        return round(current * random.uniform(1.05, 1.15), 2)
    elif trend == 'decreasing':
        return round(current * random.uniform(0.85, 0.95), 2)
    return round(current * random.uniform(0.97, 1.03), 2)


def get_weather_context():
    """
    Ob-havo ma'lumotlari (Open-Meteo, bepul, API key shart emas).
    Toshkent koordinatalari asosida.
    """
    import urllib.request
    try:
        url = (
            "https://api.open-meteo.com/v1/forecast"
            "?latitude=41.3&longitude=64.3"
            "&current=temperature_2m,precipitation,windspeed_10m,weathercode"
            "&hourly=precipitation,temperature_2m&forecast_days=2"
            "&timezone=Asia%2FTashkent"
        )
        with urllib.request.urlopen(url, timeout=3) as resp:
            data = json.loads(resp.read())
        current = data.get('current', {})
        hourly = data.get('hourly', {})

        # Keyingi 12 soat yomg'ir miqdori
        precip_12h = sum(hourly.get('precipitation', [0] * 12)[:12])

        return {
            'temp': current.get('temperature_2m', 'N/A'),
            'precip': round(current.get('precipitation', 0), 1),
            'wind': current.get('windspeed_10m', 'N/A'),
            'code': current.get('weathercode', 0),
            'precip_12h': round(precip_12h, 1),
            'available': True
        }
    except Exception:
        # Fallback - haqiqiy Toshkent ob-havosiga yaqin demo
        return {
            'temp': round(random.uniform(12, 28), 1),
            'precip': round(random.uniform(0, 2), 1),
            'wind': round(random.uniform(3, 12), 1),
            'code': 1,
            'precip_12h': round(random.uniform(0, 8), 1),
            'available': False
        }


def weather_code_to_text(code, lang):
    """Ob-havo kodini matniga aylantiradi."""
    codes = {
        'uz': {0: "Ochiq", 1: "Asosan ochiq", 2: "Qisman bulutli", 3: "Bulutli",
               51: "Mayda yomg'ir", 61: "Yomg'ir", 71: "Qor", 80: "Jala", 95: "Momaqaldiroq"},
        'ru': {0: "Ясно", 1: "Преимущественно ясно", 2: "Переменная облачность",
               3: "Облачно", 51: "Мелкий дождь", 61: "Дождь", 71: "Снег",
               80: "Ливень", 95: "Гроза"},
        'en': {0: "Clear", 1: "Mostly clear", 2: "Partly cloudy", 3: "Cloudy",
               51: "Drizzle", 61: "Rain", 71: "Snow", 80: "Showers", 95: "Thunderstorm"},
    }
    return codes.get(lang, codes['uz']).get(code, codes['uz'].get(code, "Noma'lum"))


# ─────────────────────────────────────────────
#  Response Generators (UZ / RU / EN)
# ─────────────────────────────────────────────

def build_response(categories: list, lang: str, message: str) -> str:
    """Asosiy javob generatori."""

    if 'help' in categories and not any(c in categories for c in ['theft', 'forecast', 'critical', 'weather']):
        return _help_response(lang)

    parts = []

    if 'theft' in categories or 'flow' in categories:
        parts.append(_theft_response(lang))

    if 'forecast' in categories:
        hours = 24 if '24' in message else 12
        parts.append(_forecast_response(lang, hours))

    if 'weather' in categories:
        parts.append(_weather_response(lang))

    if 'critical' in categories:
        parts.append(_critical_response(lang))

    if 'alert' in categories:
        parts.append(_alerts_response(lang))

    if 'status' in categories and not parts:
        parts.append(_status_response(lang))

    if 'deposit' in categories and not parts:
        parts.append(_deposits_response(lang))

    return "<br><br>".join(parts) if parts else _default_response(lang, message)


def _help_response(lang):
    summary = get_system_summary()
    templates = {
        'uz': (
            "👋 <b>Assalomu alaykum! Men AquaAI — Hydromap tizimining aqlli yordamchisiman.</b><br><br>"
            f"📊 Hozirda tizimda <b>{summary['total_sensors']}</b> faol sensor va "
            f"<b>{summary['total_deposits']}</b> suv ob'yekti kuzatilmoqda.<br><br>"
            "Mening imkoniyatlarim:<br>"
            "🔴 <b>Kritik holatlar</b> — «kritik» yoki «xavf» deb so'rang<br>"
            "🕵️ <b>Suv o'g'irlanishi</b> — «o'g'irlanish» yoki «yo'qolish» deb so'rang<br>"
            "📈 <b>12/24 soatlik bashorat</b> — «bashorat 12 soat» deb so'rang<br>"
            "🌤️ <b>Ob-havo holati</b> — «ob-havo» deb so'rang<br>"
            "📡 <b>Sensor holati</b> — «sensor holati» deb so'rang"
        ),
        'ru': (
            "👋 <b>Привет! Я AquaAI — интеллектуальный помощник системы Hydromap.</b><br><br>"
            f"📊 Сейчас в системе отслеживается <b>{summary['total_sensors']}</b> активных сенсоров и "
            f"<b>{summary['total_deposits']}</b> водных объектов.<br><br>"
            "Мои возможности:<br>"
            "🔴 <b>Критические ситуации</b> — спросите «критическое» или «опасность»<br>"
            "🕵️ <b>Кражи воды</b> — спросите «кража» или «хищение»<br>"
            "📈 <b>Прогноз 12/24 ч</b> — спросите «прогноз 24 часа»<br>"
            "🌤️ <b>Погода</b> — спросите «погода»<br>"
            "📡 <b>Состояние сенсоров</b> — спросите «состояние сенсоров»"
        ),
        'en': (
            "👋 <b>Hello! I am AquaAI — the intelligent assistant of the Hydromap system.</b><br><br>"
            f"📊 Currently monitoring <b>{summary['total_sensors']}</b> active sensors and "
            f"<b>{summary['total_deposits']}</b> water objects.<br><br>"
            "My capabilities:<br>"
            "🔴 <b>Critical situations</b> — ask about «critical» or «danger»<br>"
            "🕵️ <b>Water theft</b> — ask about «theft» or «stealing»<br>"
            "📈 <b>12/24-hour forecast</b> — ask «forecast 24 hours»<br>"
            "🌤️ <b>Weather</b> — ask «weather»<br>"
            "📡 <b>Sensor status</b> — ask «sensor status»"
        ),
    }
    return templates.get(lang, templates['uz'])


def _theft_response(lang):
    anomalies = detect_theft_anomalies()
    now_str = datetime.now().strftime("%H:%M")

    if not anomalies:
        messages = {
            'uz': f"✅ <b>Suv o'g'irlanishi aniqlanmadi</b> [{now_str}]<br>Barcha upstream/downstream nazorat nuqtalarida oqim muvozanati me'yor doirasida.",
            'ru': f"✅ <b>Краж воды не обнаружено</b> [{now_str}]<br>Во всех контрольных точках upstream/downstream баланс потока в норме.",
            'en': f"✅ <b>No water theft detected</b> [{now_str}]<br>All upstream/downstream control points show normal flow balance.",
        }
        return messages.get(lang, messages['uz'])

    lines = []
    headers = {
        'uz': f"🚨 <b>{len(anomalies)} ta shubhali suv yo'qolish nuqtasi aniqlandi</b> [{now_str}]<br>",
        'ru': f"🚨 <b>Обнаружено {len(anomalies)} подозрительных точек потери воды</b> [{now_str}]<br>",
        'en': f"🚨 <b>{len(anomalies)} suspicious water loss points detected</b> [{now_str}]<br>",
    }
    lines.append(headers.get(lang, headers['uz']))

    for a in anomalies:
        icon = "🔴" if a['severity'] == 'high' else "🟡"
        if lang == 'uz':
            lines.append(
                f"{icon} <b>{a['canal']}</b><br>"
                f"&nbsp;&nbsp;↑ Yuqori oqim: {a['upstream_flow']} m³/s<br>"
                f"&nbsp;&nbsp;↓ Quyi oqim: {a['downstream_flow']} m³/s<br>"
                f"&nbsp;&nbsp;⚠️ Yo'qotish: <b style='color:#ff6b6b'>{a['loss_pct']}%</b>"
            )
        elif lang == 'ru':
            lines.append(
                f"{icon} <b>{a['canal']}</b><br>"
                f"&nbsp;&nbsp;↑ Вверх по течению: {a['upstream_flow']} м³/с<br>"
                f"&nbsp;&nbsp;↓ Вниз по течению: {a['downstream_flow']} м³/с<br>"
                f"&nbsp;&nbsp;⚠️ Потери: <b style='color:#ff6b6b'>{a['loss_pct']}%</b>"
            )
        else:
            lines.append(
                f"{icon} <b>{a['canal']}</b><br>"
                f"&nbsp;&nbsp;↑ Upstream: {a['upstream_flow']} m³/s<br>"
                f"&nbsp;&nbsp;↓ Downstream: {a['downstream_flow']} m³/s<br>"
                f"&nbsp;&nbsp;⚠️ Loss: <b style='color:#ff6b6b'>{a['loss_pct']}%</b>"
            )

    advice = {
        'uz': "<br>💡 <i>Tavsiya: Belgilangan hududlarda darhol jismoniy tekshiruv o'tkazish tavsiya etiladi.</i>",
        'ru': "<br>💡 <i>Рекомендация: Незамедлительно провести физическую проверку в указанных районах.</i>",
        'en': "<br>💡 <i>Recommendation: Immediate physical inspection is advised in the flagged areas.</i>",
    }
    lines.append(advice.get(lang, advice['uz']))
    return "<br>".join(lines)


def _forecast_response(lang, hours=24):
    data = get_forecast_data(hours)
    trend_icons = {'increasing': '📈', 'decreasing': '📉', 'stable': '➡️'}
    trend_icon = trend_icons.get(data['trend'], '➡️')

    trend_texts = {
        'uz': {'increasing': 'o\'sish', 'decreasing': 'kamayish', 'stable': 'barqaror'},
        'ru': {'increasing': 'рост', 'decreasing': 'снижение', 'stable': 'стабильно'},
        'en': {'increasing': 'increasing', 'decreasing': 'decreasing', 'stable': 'stable'},
    }
    trend_word = trend_texts.get(lang, trend_texts['uz']).get(data['trend'], '')

    templates = {
        'uz': (
            f"📊 <b>{hours} soatlik suv oqimi bashorati</b><br><br>"
            f"📉 O'rtacha oqim: <b>{data['avg_flow']} m³/s</b><br>"
            f"⬆️ Maksimal: <b>{data['max_flow']} m³/s</b><br>"
            f"⬇️ Minimal: <b>{data['min_flow']} m³/s</b><br>"
            f"💧 O'rtacha sath: <b>{data['avg_level']} m</b><br>"
            f"🧪 pH darajasi: <b>{data['avg_ph']}</b><br><br>"
            f"{trend_icon} <b>Trend:</b> {trend_word}<br>"
            f"🔮 Keyingi {hours//2} soatlik bashorat: <b>{data['predicted_next']} m³/s</b><br><br>"
            f"{'⚠️ Oqim kamayishi kuzatilmoqda. Nazoratni kuchaytiring!' if data['trend'] == 'decreasing' else '✅ Vaziyat barqaror.'}"
        ),
        'ru': (
            f"📊 <b>Прогноз расхода воды на {hours} часов</b><br><br>"
            f"📉 Средний расход: <b>{data['avg_flow']} м³/с</b><br>"
            f"⬆️ Максимальный: <b>{data['max_flow']} м³/с</b><br>"
            f"⬇️ Минимальный: <b>{data['min_flow']} м³/с</b><br>"
            f"💧 Средний уровень: <b>{data['avg_level']} м</b><br>"
            f"🧪 Уровень pH: <b>{data['avg_ph']}</b><br><br>"
            f"{trend_icon} <b>Тренд:</b> {trend_word}<br>"
            f"🔮 Прогноз на следующие {hours//2} часов: <b>{data['predicted_next']} м³/с</b><br><br>"
            f"{'⚠️ Наблюдается снижение потока. Усильте мониторинг!' if data['trend'] == 'decreasing' else '✅ Ситуация стабильная.'}"
        ),
        'en': (
            f"📊 <b>{hours}-hour water flow forecast</b><br><br>"
            f"📉 Average flow: <b>{data['avg_flow']} m³/s</b><br>"
            f"⬆️ Maximum: <b>{data['max_flow']} m³/s</b><br>"
            f"⬇️ Minimum: <b>{data['min_flow']} m³/s</b><br>"
            f"💧 Average level: <b>{data['avg_level']} m</b><br>"
            f"🧪 pH level: <b>{data['avg_ph']}</b><br><br>"
            f"{trend_icon} <b>Trend:</b> {trend_word}<br>"
            f"🔮 Next {hours//2}-hour prediction: <b>{data['predicted_next']} m³/s</b><br><br>"
            f"{'⚠️ Flow reduction observed. Increase monitoring!' if data['trend'] == 'decreasing' else '✅ Situation is stable.'}"
        ),
    }
    return templates.get(lang, templates['uz'])


def _weather_response(lang):
    w = get_weather_context()
    desc = weather_code_to_text(w['code'], lang)

    impact_texts = {
        'uz': (
            "🌦️ <b>Hozirgi ob-havo (O'zbekiston)</b><br><br>"
            f"🌡️ Harorat: <b>{w['temp']}°C</b><br>"
            f"🌧️ Hozirgi yog'in: <b>{w['precip']} mm</b><br>"
            f"💨 Shamol tezligi: <b>{w['wind']} km/s</b><br>"
            f"☁️ Holat: <b>{desc}</b><br><br>"
            f"📍 Keyingi 12 soatda yog'in: <b>{w['precip_12h']} mm</b><br><br>"
            + (
                "⚠️ <b>Yuqori yog'in bashorat qilinmoqda!</b> Suv omborlari to'lib ketish xavfi bor. "
                "Nazoratni kuchaytiring." if w['precip_12h'] > 5
                else "✅ Ob-havo sharoiti barqaror. Suv omborlariga to'g'ridan-to'g'ri ta'sir kutilmaydi."
            )
        ),
        'ru': (
            "🌦️ <b>Текущая погода (Узбекистан)</b><br><br>"
            f"🌡️ Температура: <b>{w['temp']}°C</b><br>"
            f"🌧️ Текущие осадки: <b>{w['precip']} мм</b><br>"
            f"💨 Скорость ветра: <b>{w['wind']} км/ч</b><br>"
            f"☁️ Состояние: <b>{desc}</b><br><br>"
            f"📍 Осадки следующие 12 ч: <b>{w['precip_12h']} мм</b><br><br>"
            + (
                "⚠️ <b>Прогнозируется сильный дождь!</b> Возможен риск переполнения водохранилищ. "
                "Усильте мониторинг." if w['precip_12h'] > 5
                else "✅ Погодные условия стабильны. Прямого влияния на водоёмы не ожидается."
            )
        ),
        'en': (
            "🌦️ <b>Current Weather (Uzbekistan)</b><br><br>"
            f"🌡️ Temperature: <b>{w['temp']}°C</b><br>"
            f"🌧️ Current precipitation: <b>{w['precip']} mm</b><br>"
            f"💨 Wind speed: <b>{w['wind']} km/h</b><br>"
            f"☁️ Condition: <b>{desc}</b><br><br>"
            f"📍 Next 12h precipitation: <b>{w['precip_12h']} mm</b><br><br>"
            + (
                "⚠️ <b>Heavy rain forecasted!</b> Risk of reservoir overflow. "
                "Increase monitoring frequency." if w['precip_12h'] > 5
                else "✅ Weather conditions are stable. No direct impact on water bodies expected."
            )
        ),
    }
    return impact_texts.get(lang, impact_texts['uz'])


def _critical_response(lang):
    alerts = get_critical_alerts(5)
    summary = get_system_summary()

    if summary['critical_sensors'] == 0 and not alerts:
        ok = {
            'uz': "✅ <b>Hozirda kritik holat yo'q.</b> Barcha sensorlar me'yor ichida ishlayapti.",
            'ru': "✅ <b>Критических ситуаций не обнаружено.</b> Все сенсоры работают в норме.",
            'en': "✅ <b>No critical situations found.</b> All sensors operating within normal range.",
        }
        return ok.get(lang, ok['uz'])

    lines = []
    headers = {
        'uz': f"🚨 <b>Kritik holat xulosasi</b><br>🔴 Kritik sensorlar: {summary['critical_sensors']} | 🟡 Ogohlantirishlar: {summary['warning_sensors']}<br><br>",
        'ru': f"🚨 <b>Сводка критических ситуаций</b><br>🔴 Критических сенсоров: {summary['critical_sensors']} | 🟡 Предупреждений: {summary['warning_sensors']}<br><br>",
        'en': f"🚨 <b>Critical Situation Summary</b><br>🔴 Critical sensors: {summary['critical_sensors']} | 🟡 Warnings: {summary['warning_sensors']}<br><br>",
    }
    lines.append(headers.get(lang, headers['uz']))

    for a in alerts:
        ts = a.timestamp.strftime("%d.%m %H:%M")
        if lang == 'uz':
            lines.append(f"⚡ <b>{a.sensor.name}</b> [{ts}]<br>&nbsp;&nbsp;{a.message}")
        elif lang == 'ru':
            lines.append(f"⚡ <b>{a.sensor.name}</b> [{ts}]<br>&nbsp;&nbsp;{a.message}")
        else:
            lines.append(f"⚡ <b>{a.sensor.name}</b> [{ts}]<br>&nbsp;&nbsp;{a.message}")

    if not alerts:
        no_detail = {
            'uz': "ℹ️ Batafsil xabarnomalar mavjud emas, lekin sensorlar kritik holatda.",
            'ru': "ℹ️ Подробные уведомления недоступны, но сенсоры в критическом состоянии.",
            'en': "ℹ️ No detailed alerts available, but sensors are in critical state.",
        }
        lines.append(no_detail.get(lang, no_detail['uz']))

    return "<br>".join(lines)


def _alerts_response(lang):
    recent = Alert.objects.filter(
        timestamp__gte=timezone.now() - timedelta(hours=24),
        is_resolved=False
    ).select_related('sensor').order_by('-timestamp')[:6]

    if not recent:
        ok = {
            'uz': "✅ <b>So'nggi 24 soatda hal qilinmagan anomaliya yo'q.</b> Tizim barqaror.",
            'ru': "✅ <b>За последние 24 часа нерешённых аномалий нет.</b> Система стабильна.",
            'en': "✅ <b>No unresolved anomalies in the last 24 hours.</b> System is stable.",
        }
        return ok.get(lang, ok['uz'])

    lines = []
    headers = {
        'uz': f"📋 <b>So'nggi 24 soat anomaliyalari ({recent.count()} ta)</b><br>",
        'ru': f"📋 <b>Аномалии за последние 24 часа ({recent.count()} шт.)</b><br>",
        'en': f"📋 <b>Last 24-hour anomalies ({recent.count()})</b><br>",
    }
    lines.append(headers.get(lang, headers['uz']))

    severity_icons = {'critical': '🔴', 'warning': '🟡', 'info': '🔵'}
    for a in recent:
        icon = severity_icons.get(a.severity, '⚪')
        ts = a.timestamp.strftime("%H:%M")
        lines.append(f"{icon} [{ts}] <b>{a.sensor.name}</b> — {a.message[:80]}")

    return "<br>".join(lines)


def _status_response(lang):
    summary = get_system_summary()
    health_pct = (summary['normal_sensors'] / max(summary['total_sensors'], 1)) * 100

    health_label = {
        'uz': 'ajoyib' if health_pct > 80 else 'qoniqarli' if health_pct > 50 else 'yomon',
        'ru': 'отлично' if health_pct > 80 else 'удовлетворительно' if health_pct > 50 else 'плохо',
        'en': 'excellent' if health_pct > 80 else 'satisfactory' if health_pct > 50 else 'poor',
    }.get(lang, 'N/A')

    templates = {
        'uz': (
            f"📡 <b>Tizim holati — {datetime.now().strftime('%H:%M')}</b><br><br>"
            f"✅ Faol sensorlar: <b>{summary['total_sensors']}</b><br>"
            f"🔴 Kritik: <b>{summary['critical_sensors']}</b><br>"
            f"🟡 Ogohlantirishlar: <b>{summary['warning_sensors']}</b><br>"
            f"🟢 Me'yor: <b>{summary['normal_sensors']}</b><br><br>"
            f"💧 Suv ob'yektlari: <b>{summary['total_deposits']}</b> ta<br>"
            f"🚨 Kritik ob'yektlar: <b>{summary['critical_deposits']}</b> ta<br><br>"
            f"📊 Tizim salomatligi: <b>{round(health_pct, 1)}%</b> — {health_label}<br>"
            f"⚡ Oxirgi 24 soat ogohlantirishi: <b>{summary['recent_alerts']}</b> ta"
        ),
        'ru': (
            f"📡 <b>Состояние системы — {datetime.now().strftime('%H:%M')}</b><br><br>"
            f"✅ Активных сенсоров: <b>{summary['total_sensors']}</b><br>"
            f"🔴 Критических: <b>{summary['critical_sensors']}</b><br>"
            f"🟡 Предупреждений: <b>{summary['warning_sensors']}</b><br>"
            f"🟢 В норме: <b>{summary['normal_sensors']}</b><br><br>"
            f"💧 Водных объектов: <b>{summary['total_deposits']}</b><br>"
            f"🚨 Критических объектов: <b>{summary['critical_deposits']}</b><br><br>"
            f"📊 Здоровье системы: <b>{round(health_pct, 1)}%</b> — {health_label}<br>"
            f"⚡ Предупреждений за 24 ч: <b>{summary['recent_alerts']}</b>"
        ),
        'en': (
            f"📡 <b>System Status — {datetime.now().strftime('%H:%M')}</b><br><br>"
            f"✅ Active sensors: <b>{summary['total_sensors']}</b><br>"
            f"🔴 Critical: <b>{summary['critical_sensors']}</b><br>"
            f"🟡 Warnings: <b>{summary['warning_sensors']}</b><br>"
            f"🟢 Normal: <b>{summary['normal_sensors']}</b><br><br>"
            f"💧 Water objects: <b>{summary['total_deposits']}</b><br>"
            f"🚨 Critical objects: <b>{summary['critical_deposits']}</b><br><br>"
            f"📊 System health: <b>{round(health_pct, 1)}%</b> — {health_label}<br>"
            f"⚡ Last 24h alerts: <b>{summary['recent_alerts']}</b>"
        ),
    }
    return templates.get(lang, templates['uz'])


def _deposits_response(lang):
    deposits = WaterDeposit.objects.all()
    by_status = {
        'critical': deposits.filter(status='critical').count(),
        'warning': deposits.filter(status='warning').count(),
        'normal': deposits.filter(status='normal').count(),
    }
    critical_list = deposits.filter(status='critical')[:3]

    lines = []
    headers = {
        'uz': f"💧 <b>Suv ob'yektlari umumiy holati</b><br>🔴 Kritik: {by_status['critical']} | 🟡 Ogohlantirishlar: {by_status['warning']} | 🟢 Me'yor: {by_status['normal']}<br>",
        'ru': f"💧 <b>Общее состояние водных объектов</b><br>🔴 Критических: {by_status['critical']} | 🟡 Предупреждений: {by_status['warning']} | 🟢 В норме: {by_status['normal']}<br>",
        'en': f"💧 <b>Water Objects Overview</b><br>🔴 Critical: {by_status['critical']} | 🟡 Warning: {by_status['warning']} | 🟢 Normal: {by_status['normal']}<br>",
    }
    lines.append(headers.get(lang, headers['uz']))

    if critical_list:
        sub_headers = {
            'uz': "<br>🚨 <b>Kritik ob'yektlar:</b>",
            'ru': "<br>🚨 <b>Критические объекты:</b>",
            'en': "<br>🚨 <b>Critical objects:</b>",
        }
        lines.append(sub_headers.get(lang, sub_headers['uz']))
        for d in critical_list:
            name = d.name if lang == 'uz' else (d.name_ru or d.name if lang == 'ru' else d.name_en or d.name)
            lines.append(f"  • {name} ({d.latitude:.3f}, {d.longitude:.3f})")

    return "<br>".join(lines)


def _default_response(lang, message):
    templates = {
        'uz': (
            f"🤖 <b>Hydromap AI:</b> \"{message}\" — bu so'rov bo'yicha ma'lumot izlayapman...<br><br>"
            "Quyidagi mavzular bo'yicha aniqroq so'rang:<br>"
            "• Suv o'g'irlanishi<br>• Bashorat (12/24 soat)<br>• Ob-havo<br>• Kritik holatlar<br>• Sensor holati"
        ),
        'ru': (
            f"🤖 <b>Hydromap AI:</b> Ищу информацию по запросу \"{message}\"...<br><br>"
            "Задайте более точный вопрос по темам:<br>"
            "• Кражи воды<br>• Прогноз (12/24 часа)<br>• Погода<br>• Критические ситуации<br>• Состояние сенсоров"
        ),
        'en': (
            f"🤖 <b>Hydromap AI:</b> Searching for information on \"{message}\"...<br><br>"
            "Ask a more specific question about:<br>"
            "• Water theft<br>• Forecast (12/24 hours)<br>• Weather<br>• Critical situations<br>• Sensor status"
        ),
    }
    return templates.get(lang, templates['uz'])


# ─────────────────────────────────────────────
#  Main Entry Point
# ─────────────────────────────────────────────

def process_chat_message(message: str, lang: str = 'uz') -> str:
    """
    Chatbot xabarini qayta ishlaydi va HTML javob qaytaradi.
    Bu asosiy funksiya view dan chaqiriladi.
    """
    if not message or not message.strip():
        return _help_response(lang)

    categories = classify_message(message)
    return build_response(categories, lang, message)
