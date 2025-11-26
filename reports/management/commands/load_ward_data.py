# reports/management/commands/load_ward_data.py
import json
from django.core.management.base import BaseCommand
from reports.models import Ward

class Command(BaseCommand):
    help = "Load Ahmedabad wards from fixtures/wards.json"

    def handle(self, *args, **options):
        path = "reports/fixtures/wards.json"
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        created = 0
        for item in data:
            obj, was_created = Ward.objects.update_or_create(
                ward_number=item["ward_number"],
                defaults={
                    "ward_name": item["ward_name"],
                    "zone": item["zone"],
                    "officer_name": item.get("officer_name", ""),
                    "officer_email": item.get("officer_email", ""),
                    "officer_phone": item.get("officer_phone", ""),
                },
            )
            created += 1 if was_created else 0
        self.stdout.write(self.style.SUCCESS(f"Loaded {len(data)} wards (created {created})."))