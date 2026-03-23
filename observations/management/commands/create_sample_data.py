from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from observations.models import School, Teacher


class Command(BaseCommand):
    help = 'Creates sample schools, teachers, and a superuser for development'

    def handle(self, *args, **options):
        # Create superuser if none exists
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                username='admin',
                password='admin123',
                email='admin@example.com'
            )
            self.stdout.write(self.style.SUCCESS('Superuser created: admin / admin123'))
        else:
            self.stdout.write('Superuser already exists, skipping.')

        # Sample data: school name -> list of (teacher name, teacher_id)
        sample_data = {
            'Archer City Elementary': [
                ('Maria Gonzalez', 'V5T-23020211'),
                ('James Holloway', 'V5T-23020212'),
                ('Patricia Reyes', 'V5T-23020213'),
            ],
            'Lincoln Middle School': [
                ('David Chen', 'LMS-23030101'),
                ('Sandra Williams', 'LMS-23030102'),
                ('Robert Martinez', 'LMS-23030103'),
            ],
            'Roosevelt High School': [
                ('Angela Thompson', 'RHS-23040201'),
                ('Michael Brown', 'RHS-23040202'),
            ],
        }

        for school_name, teachers in sample_data.items():
            school, created = School.objects.get_or_create(name=school_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created school: {school_name}'))
            else:
                self.stdout.write(f'School already exists: {school_name}')

            for teacher_name, teacher_id in teachers:
                teacher, t_created = Teacher.objects.get_or_create(
                    teacher_id=teacher_id,
                    defaults={'name': teacher_name, 'school': school}
                )
                if t_created:
                    self.stdout.write(self.style.SUCCESS(f'  Created teacher: {teacher_name} ({teacher_id})'))
                else:
                    self.stdout.write(f'  Teacher already exists: {teacher_name} ({teacher_id})')

        self.stdout.write(self.style.SUCCESS('\nSample data setup complete.'))
        self.stdout.write('You can log in at http://127.0.0.1:8000/login/ with admin / admin123')
