
from django.core.management.base import BaseCommand
from django.db import transaction

from complaints.models import Complaint
from complaints.ai_engine import analyze_complaint


class Command(BaseCommand):
    help = "Create 40 synthetic CivicTrack AI demo complaints"

    def handle(self, *args, **options):

        # Four separate demonstration areas
        areas = [
            {
                "name": "Demo Zone A, Bengaluru",
                "latitude": 12.9716,
                "longitude": 77.5946,
            },
            {
                "name": "Demo Zone B, Bengaluru",
                "latitude": 12.9816,
                "longitude": 77.6046,
            },
            {
                "name": "Demo Zone C, Bengaluru",
                "latitude": 12.9616,
                "longitude": 77.5846,
            },
            {
                "name": "Demo Zone D, Bengaluru",
                "latitude": 12.9916,
                "longitude": 77.5746,
            },
        ]

        # Two reports for each issue type in every area
        issues = [
            {
                "category": "Road Damage",
                "title": "Severe pothole on main road",
                "description": (
                    "A severe pothole is present on the main road "
                    "and creates a dangerous road condition for vehicles."
                ),
            },
            {
                "category": "Waterlogging",
                "title": "Heavy waterlogging near junction",
                "description": (
                    "Heavy flooding and standing water are reported "
                    "near the junction, making travel difficult."
                ),
            },
            {
                "category": "Garbage",
                "title": "Garbage overflowing near public area",
                "description": (
                    "Garbage and waste are overflowing near the "
                    "public area and need sanitation attention."
                ),
            },
            {
                "category": "Streetlight",
                "title": "Streetlight not working",
                "description": (
                    "The streetlight is not working and the road "
                    "becomes dark during the night."
                ),
            },
            {
                "category": "Drainage",
                "title": "Open manhole near residential road",
                "description": (
                    "An open manhole is present near the residential "
                    "road and creates a serious safety hazard."
                ),
            },
        ]

        statuses = [
            "Submitted",
            "Assigned",
            "In Progress",
            "Resolved",
        ]

        # Small coordinate changes keep reports close together
        offsets = [
            (0.0000, 0.0000),
            (0.0003, 0.0002),
            (0.0005, 0.0001),
            (0.0002, 0.0005),
            (0.0004, 0.0004),
            (0.0001, 0.0003),
            (0.0006, 0.0002),
            (0.0003, 0.0006),
            (0.0005, 0.0005),
            (0.0002, 0.0001),
        ]

        with transaction.atomic():

            # Remove only records created by this demo script
            deleted_count, _ = Complaint.objects.filter(
                title__startswith="[DEMO]"
            ).delete()

            self.stdout.write(
                f"Removed {deleted_count} previous demo records."
            )

            created_count = 0

            for area_index, area in enumerate(areas):

                for issue_index, issue in enumerate(issues):

                    # Create two similar reports for each issue
                    for repeat in range(2):

                        offset_index = issue_index * 2 + repeat
                        lat_offset, lon_offset = offsets[offset_index]

                        complaint = Complaint.objects.create(
                            title="[DEMO] " + issue["title"],
                            description=issue["description"],
                            category=issue["category"],
                            location=area["name"],
                            latitude=area["latitude"] + lat_offset,
                            longitude=area["longitude"] + lon_offset,
                            status=statuses[
                                (area_index + issue_index + repeat) % 4
                            ],
                        )

                        # Run the existing complaint analysis
                        analyze_complaint(complaint)

                        created_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully created {created_count} "
                    "synthetic complaints."
                )
            )
