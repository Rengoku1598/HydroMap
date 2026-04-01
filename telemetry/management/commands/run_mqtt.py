from django.core.management.base import BaseCommand
from telemetry.mqtt_handler import run_mqtt

class Command(BaseCommand):
    help = 'Runs the MQTT subscriber to ingest sensor data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting MQTT Subscriber...'))
        try:
            run_mqtt()
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('MQTT Subscriber stopped.'))
