import json
import paho.mqtt.client as mqtt
from django.utils import timezone
from sensors.models import Sensor
from .models import Hydrometry

def on_connect(client, userdata, flags, rc):
    print(f"Connected to Mosquitto with result code {rc}")
    client.subscribe("sensors/+/telemetry")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        sensor_uid = msg.topic.split('/')[1]
        
        sensor = Sensor.objects.get(uid=sensor_uid)
        
        # Save reading
        Hydrometry.objects.create(
            sensor=sensor,
            timestamp=timezone.now(),
            flow_rate=payload.get('flow'),
            water_level=payload.get('level'),
            ph_level=payload.get('ph'),
            turbidity=payload.get('turbidity')
        )
        print(f"Data saved for {sensor.name}")
        
    except Sensor.DoesNotExist:
        print(f"Warning: Sensor with UID {sensor_uid} not found in DB.")
    except Exception as e:
        print(f"Error processing MQTT data: {e}")

def run_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    
    # Use 'mosquitto' as host because it's the service name in docker-compose
    client.connect("mosquitto", 1883, 60)
    client.loop_forever()
