import json
import time
import random
import paho.mqtt.client as mqtt
from django.core.management.base import BaseCommand
from sensors.models import Sensor

class Command(BaseCommand):
    help = 'Simulates MQTT data from sensors'

    def handle(self, *args, **options):
        client = mqtt.Client()
        client.connect("mosquitto", 1883, 60)
        
        sensors = Sensor.objects.filter(is_active=True)
        if not sensors.exists():
            self.stdout.write(self.style.WARNING("No active sensors found in DB. Add them in Admin panel first."))
            return

        self.stdout.write(self.style.SUCCESS("Starting simulation... (Ctrl+C to stop)"))
        
        try:
            while True:
                for sensor in sensors:
                    # Simulate slightly fluctuating data
                    flow = sensor.max_flow_rate * random.uniform(0.7, 0.9)
                    
                    # Occasionally simulate a "Water Interception" (low flow)
                    if random.random() < 0.1: # 10% chance
                        flow = sensor.max_flow_rate * 0.4 
                    
                    payload = {
                        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                        "flow": round(flow, 2),
                        "level": round(random.uniform(0.5, 2.5), 2),
                        "ph": round(random.uniform(6.8, 7.5), 1),
                        "turbidity": round(random.uniform(10, 80), 0)
                    }
                    
                    topic = f"sensors/{sensor.uid}/telemetry"
                    client.publish(topic, json.dumps(payload))
                    self.stdout.write(f"Published to {topic}: {payload['flow']} m3/s")
                
                time.sleep(10) # Wait 10 seconds before next reading
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS("Simulation stopped."))
