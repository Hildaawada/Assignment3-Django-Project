import csv
from django.core.management.base import BaseCommand
from contact_app.models import Professional

class Command(BaseCommand):
    help = 'Import contacts from a CSV file into the Professional model'

    def handle(self, *args, **kwargs):
        file_path = r"C:\Users\USAID\OneDrive - American University of Beirut\Desktop\final_updated_people_random_states.csv"
        try:
            with open(file_path, mode='r') as file:
                reader = csv.DictReader(file)
                professionals = []
                for row in reader:
                    professionals.append(
                        Professional(
                            first_name=row['First Name'],
                            last_name=row['Last Name'],
                            email=row['Email'],
                            phone=row['Phone'],
                            state=row['States'],
                            expertise=row['Expertise'],
                            job_title=row['Job Title'],
                            service_cost_per_hour=row['Service Cost per Hour']
                        )
                    )
                Professional.objects.bulk_create(professionals)
                self.stdout.write(self.style.SUCCESS(f"Successfully imported {len(professionals)} records."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error importing data: {e}"))
