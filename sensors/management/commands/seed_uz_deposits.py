from django.core.management.base import BaseCommand
from sensors.models import WaterDeposit

class Command(BaseCommand):
    help = 'Seeds major Uzbekistan reservoirs into the database'

    def handle(self, *args, **options):
        # Coordinates for major Uzbekistan reservoirs
        deposits = [
            {
                'name': 'Chorvoq Suv Ombori (Charvak)',
                'deposit_type': 'reservoir',
                'latitude': 41.6444,
                'longitude': 70.0333,
                'radius_meters': 8000,
                'status': 'normal',
                'description': 'Toshkent viloyatidagi eng yirik gidrotexnika inshooti. Chirchiq daryosi havzasida joylashgan.'
            },
            {
                'name': 'Tuyabo\'g\'iz Suv Ombori (Tashkent Sea)',
                'deposit_type': 'reservoir',
                'latitude': 41.0500,
                'longitude': 69.3167,
                'radius_meters': 5000,
                'status': 'warning',
                'description': 'Toshkent viloyatida joylashgan, Ohangaron daryosi suvidan foydalaniladi. Sug\'orish uchun muhim.'
            },
            {
                'name': 'Andijon Suv Ombori (Kampirravot)',
                'deposit_type': 'reservoir',
                'latitude': 40.8500,
                'longitude': 73.0000,
                'radius_meters': 6000,
                'status': 'critical',
                'description': 'Qoradaryo havzasida joylashgan. Chegara hududida monitoring talab etiladi.'
            },
            {
                'name': 'Pachkamar Suv Ombori',
                'deposit_type': 'reservoir',
                'latitude': 38.4500,
                'longitude': 66.5000,
                'radius_meters': 3500,
                'status': 'normal',
                'description': 'Qashqadaryo viloyatida joylashgan suv ob\'yekti.'
            },
            {
                'name': 'G\'issarak Suv Ombori',
                'deposit_type': 'reservoir',
                'latitude': 38.8667,
                'longitude': 67.1333,
                'radius_meters': 3000,
                'status': 'normal',
                'description': 'Qashqadaryo viloyati Shahrisabz tumanidagi suv ombori.'
            }
        ]

        for data in deposits:
            obj, created = WaterDeposit.objects.update_or_create(
                name=data['name'],
                defaults=data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created: {data['name']}"))
            else:
                self.stdout.write(self.style.WARNING(f"Updated: {data['name']}"))

        self.stdout.write(self.style.SUCCESS('Successfully seeded Uzbekistan water deposits.'))
