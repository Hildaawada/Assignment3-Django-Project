import csv
from django.core.management.base import BaseCommand
from contact_app.models import Professional

class Command(BaseCommand):
    help = 'Update job titles for existing professionals using a CSV file'

    def handle(self, *args, **kwargs):
        file_path = r"C:\Users\mohdf\Downloads\final_updated_people_random_states.csv"
        try:
            with open(file_path, mode='r') as file:
                reader = csv.DictReader(file)
                updated_count = 0
                skipped_count = 0

                for row in reader:
                    try:
                        # Match the record using email
                        professional = Professional.objects.get(email=row['Email'])

                        # Update the job_title field
                        professional.job_title = row['Job Title']
                        professional.save()

                        updated_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f"Updated job title for: {row['Email']}")
                        )
                    except Professional.DoesNotExist:
                        skipped_count += 1
                        self.stdout.write(
                            self.style.WARNING(f"Email not found, skipped: {row['Email']}")
                        )
                    except Exception as e:
                        self.stderr.write(self.style.ERROR(f"Error updating {row['Email']}: {e}"))

                self.stdout.write(
                    self.style.SUCCESS(f"Successfully updated {updated_count} records.")
                )
                self.stdout.write(
                    self.style.WARNING(f"Skipped {skipped_count} records (email not found).")
                )
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error reading the CSV file: {e}"))
