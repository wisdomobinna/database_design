import os
import glob
from django.db import connection
from django.core.management.base import BaseCommand
from main.data_files.init_database import load_tables, table_init

class Command(BaseCommand):
    help = "Automatically import CSV data into the database if not already imported."

    def is_data_imported():
      with connection.cursor() as cursor:
          cursor.execute("SELECT COUNT(*) FROM crime;")
          count = cursor.fetchone()[0]
      return count > 0


    def handle(self, *args, **options):
        table_init() # Error proofed with IF NOT EXISTS

        with connection.cursor() as cursor:
          cursor.execute("SELECT COUNT(*) FROM crime;")
          count = cursor.fetchone()[0]

        # Check if data has already been imported by inspecting the crime table.
        if count == 0:
            # Set the directory where your CSV files reside.
            # Adjust the path so it correctly points to your data_files directory.
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            csv_directory = os.path.join(BASE_DIR, "..", "..", "data_files")
            
            master_file = None
            csv_files = glob.glob(os.path.join(csv_directory, "*.csv"))
            
            # Process all CSV files except "crime.csv" first.
            for csv_file in csv_files:
                if os.path.basename(csv_file).lower() == "crime.csv":
                    master_file = csv_file
                else:
                    load_tables(csv_file)
            
            # Process "crime.csv" last due to foreign key dependencies.
            if master_file:
                load_tables(master_file)
            
            self.stdout.write(self.style.SUCCESS("CSV data imported successfully."))
        else:
            self.stdout.write("Data already imported, skipping.")
