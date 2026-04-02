from django.db import models

class Sensor(models.Model):
    STATUS_CHOICES = [
        ('normal', '✅ Me\'yor'),
        ('warning', '⚠️ Ogohlantirish'),
        ('critical', '🚨 KRITIK'),
    ]

    uid = models.CharField("Qurilma ID", max_length=50, primary_key=True)
    name = models.CharField("Post nomi", max_length=150)
    canal_name = models.CharField("Kanal nomi", max_length=100)
    
    latitude = models.FloatField("Kenglik")
    longitude = models.FloatField("Uzoqlik")

    upstream_sensor = models.ForeignKey(
        'self', null=True, blank=True, 
        on_delete=models.SET_NULL, 
        related_name='downstream_sensors',
        verbose_name="Yuqori oqimdagi datchik"
    )

    max_flow_rate = models.FloatField("Maks. o'tkazuvchanlik qobiliyati (m3/s)", default=10.0)
    min_flow_rate = models.FloatField("Min. ruxsat etilgan oqim (m3/s)", default=0.5)

    status = models.CharField("Joriy holat", max_length=20, choices=STATUS_CHOICES, default='normal')
    is_active = models.BooleanField("Faol", default=True)
    last_update = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Datchik"
        verbose_name_plural = "Datchiklar"

    def __str__(self):
        return f"{self.name} [{self.uid}]"


class WaterDeposit(models.Model):
    DEPOSIT_TYPES = [
        ('reservoir', 'Suv ombori'),
        ('lake', 'Ko\'l'),
        ('groundwater', 'Yer osti suvlari'),
    ]

    STATUS_CHOICES = [
        ('normal', '✅ Me\'yor'),
        ('warning', '⚠️ Ogohlantirish'),
        ('critical', '🚨 KRITIK'),
    ]

    name = models.CharField("Nomi (UZ)", max_length=200)
    name_ru = models.CharField("Название (RU)", max_length=200, blank=True, null=True)
    name_en = models.CharField("Name (EN)", max_length=200, blank=True, null=True)

    deposit_type = models.CharField("Turi", max_length=20, choices=DEPOSIT_TYPES, default='reservoir')
    
    latitude = models.FloatField("Kenglik")
    longitude = models.FloatField("Uzoqlik")
    radius_meters = models.FloatField("Radius (metr)", default=5000)

    status = models.CharField("Holati", max_length=20, choices=STATUS_CHOICES, default='normal')
    
    description = models.TextField("Tavsif (UZ)", blank=True)
    description_ru = models.TextField("Описание (RU)", blank=True, null=True)
    description_en = models.TextField("Description (EN)", blank=True, null=True)

    class Meta:
        verbose_name = "Suv ob'yekti"
        verbose_name_plural = "Suv ob'yektlari"

    def __str__(self):
        return self.name


class Hydrometry(models.Model):
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, related_name='telemetry')
    timestamp = models.DateTimeField("Sana va vaqt", db_index=True)
    
    flow_rate = models.FloatField("Suv sarfi (m3/s)", null=True)
    water_level = models.FloatField("Suv sathi (m)", null=True)
    
    ph_level = models.FloatField("pH darajasi", null=True, default=7.0)
    turbidity = models.FloatField("Loyqalik (NTU)", null=True)

    class Meta:
        verbose_name = "Gidroko'rsatkich"
        verbose_name_plural = "Gidroko'rsatkichlar tarixi"
        ordering = ['-timestamp']


class Alert(models.Model):
    SEVERITY_CHOICES = [
        ('info', 'ℹ️ Info'),
        ('warning', '⚠️ Ogohlantirish'),
        ('critical', '🚨 KRITIK'),
    ]

    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField("Anomaliya turi", max_length=50)
    severity = models.CharField("Daraja", max_length=20, choices=SEVERITY_CHOICES, default='warning')
    message = models.TextField("Anomaliya haqida xabar")
    
    timestamp = models.DateTimeField("Voqea sanasi", auto_now_add=True)
    is_resolved = models.BooleanField("Hal qilindi", default=False)
    resolved_at = models.DateTimeField("Hal qilingan sana", null=True, blank=True)

    class Meta:
        verbose_name = "Xabarnoma"
        verbose_name_plural = "Xabarnomalar"
        ordering = ['-timestamp']
