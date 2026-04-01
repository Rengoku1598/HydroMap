from django.db import models
from sensors.models import Sensor

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
