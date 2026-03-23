import csv
import os
import re
from django.core.management.base import BaseCommand
from observations.models import School, Teacher


def slugify_id(name, school_name):
    """Generate a teacher ID from initials and school abbreviation."""
    parts = name.strip().split()
    initials = ''.join(p[0].upper() for p in parts if p)
    abbr = ''.join(w[0].upper() for w in school_name.split()[:3])
    return f"{abbr}-{initials}"


class Command(BaseCommand):
    help = 'Import schools and teachers from VICTORY Teachers CSV'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            nargs='?',
            default=os.path.join(os.path.dirname(__file__), '../../../../VICTORY Teachers (G5).csv'),
            help='Path to the CSV file',
        )

    def handle(self, *args, **options):
        csv_path = os.path.abspath(options['csv_file'])
        if not os.path.exists(csv_path):
            self.stderr.write(f"File not found: {csv_path}")
            return

        created_schools = 0
        created_teachers = 0
        skipped = 0

        with open(csv_path, newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                district = row.get('District', '').strip()
                campus = row.get('Campus', '').strip()
                condition = row.get('Condition', '').strip()
                teacher_name = row.get('Teacher', '').strip()

                if not campus or not teacher_name:
                    continue

                school, s_created = School.objects.get_or_create(
                    name=campus,
                    defaults={'district': district, 'condition': condition},
                )
                if s_created:
                    created_schools += 1
                    self.stdout.write(f"  Created school: {campus}")

                # Generate a unique teacher_id
                base_id = slugify_id(teacher_name, campus)
                teacher_id = base_id
                suffix = 1
                while Teacher.objects.filter(teacher_id=teacher_id).exists():
                    teacher_id = f"{base_id}{suffix}"
                    suffix += 1

                _, t_created = Teacher.objects.get_or_create(
                    name=teacher_name,
                    school=school,
                    defaults={'teacher_id': teacher_id},
                )
                if t_created:
                    created_teachers += 1
                    self.stdout.write(f"    + Teacher: {teacher_name} ({teacher_id})")
                else:
                    skipped += 1

        self.stdout.write(self.style.SUCCESS(
            f"\nDone. Created {created_schools} schools, {created_teachers} teachers. "
            f"Skipped {skipped} existing."
        ))
