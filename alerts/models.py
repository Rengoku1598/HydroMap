from django.db import models
from sensors.models import Sensor

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
