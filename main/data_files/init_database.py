import os
# import pandas as pd
from django.db import connection

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def table_init():
    """Creates tables if they don't exist using the provided SQL schema."""
    sql_file_path = os.path.join(BASE_DIR, "create.sql")
    with open(sql_file_path, "r", encoding="utf-8") as file:
        sql_script = file.read()
    with connection.cursor() as cursor:
        for statement in sql_script.split(";"):
            statement = statement.strip()
            if statement:
                try:
                    cursor.execute(statement + ";")
                except Exception as e:
                    print(f"Skipping error in SQL execution: {e}")
    print("Database tables initialized.")

def create_staging_table():
    """
    Creates the staging table for raw crime data.
    Note: Extra columns (e.g. locationid, timeid, etc.) are added to store FK values.
    """
    sql = """
    CREATE TABLE IF NOT EXISTS staging_crime (
        date TEXT,
        arrest TEXT,
        year TEXT,
        latitude TEXT,
        longitude TEXT,
        time TEXT,
        day TEXT,
        month TEXT,
        area TEXT,
        crime_desc TEXT,
        premis_desc TEXT,
        crime_category TEXT,
        premis_descrip TEXT,
        locationid INTEGER,
        timeid INTEGER,
        crimecategoryid INTEGER,
        crimetypeid INTEGER,
        premisetypeid INTEGER,
        city VARCHAR(10),
        norm_area TEXT
    );
    """
    with connection.cursor() as cursor:
        cursor.execute(sql)
    print("Staging table created.")

def clean_raw_csv(raw_csv_path, city):
    """Load, clean, and enrich the raw CSV into a DataFrame."""
    df = pd.read_csv(raw_csv_path)
    
    # Standardize column names to lowercase and strip whitespace
    df.columns = [col.strip().lower() for col in df.columns]
    
    # Clean/normalize individual columns:
    df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.strftime('%Y-%m-%d')
    df['time'] = df['time'].astype(str).apply(lambda x: x if len(x.split(':')) == 3 else f"{x}:00")
    df['arrest'] = df['arrest'].astype(str).str.lower().map({'true': '1', 'false': '0'}).fillna('0')
    df['area'] = df['area'].astype(str).str.strip().str.lower()
    # Convert latitude/longitude to numeric; non-numeric become NaN
    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
    
    # Add the city column
    df['city'] = city
    
    # Precompute normalized area (if needed)
    df['norm_area'] = df['area']
    
    # If any expected column is missing from the raw CSV, add it with a default value.
    expected_cols = [
        'date', 'arrest', 'year', 'latitude', 'longitude', 'time',
        'day', 'month', 'area', 'crime desc', 'premis desc', 'crime category',
        'premis descrip', 'city', 'norm_area'
    ]
    
    # Standardize expected column names to match our convention.
    # You might want to change spaces to underscores if needed.
    # For this example, we'll assume the raw CSV uses spaces.
    for col in expected_cols:
        if col not in df.columns:
            df[col] = ""  # or pd.NA if you prefer NULLs
    
    # Reorder the DataFrame to match the expected order.
    df = df[expected_cols]
    
    return df

def export_clean_csv(raw_csv_path, city):
    """
    Cleans the raw CSV, adds missing columns if needed, and writes it out to a file.
    Returns the path to the cleaned CSV.
    """
    create_staging_table()  # Ensure the staging table exists
    
    output_file = os.path.join(BASE_DIR, f"cleaned_{city}_crime_data.csv")
    df = clean_raw_csv(raw_csv_path, city)
    
    # Write to CSV with the standardized column order.
    df.to_csv(output_file, index=False)
    print(f"Cleaned CSV exported to {output_file}")

    load_clean_csv_to_staging(output_file)
    return output_file


def load_clean_csv_to_staging(csv_file_path):
    with open(csv_file_path, 'r', encoding='utf-8') as f:
        with connection.cursor() as cursor:
            copy_sql = """
                COPY staging_crime(
                    date, arrest, year, latitude, longitude, time, day, month, 
                    area, crime_desc, premis_desc, crime_category, premis_descrip, city, norm_area
                )
                FROM STDIN WITH (FORMAT csv, HEADER true)
            """
            cursor.copy_expert(copy_sql, f)
    connection.commit()
    print("CSV data loaded into staging_crime.")

def load_tables(csv_file_path):
    table_name = os.path.splitext(os.path.basename(csv_file_path))[0]
    with open(csv_file_path, 'r', encoding='utf-8') as f:
        with connection.cursor() as cursor:
            copy_sql = f"COPY {table_name} FROM STDIN WITH (FORMAT csv, HEADER true)"
            cursor.copy_expert(copy_sql, f)
    connection.commit()