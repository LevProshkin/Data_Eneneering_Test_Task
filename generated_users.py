#Data extraction
import pandas as pd
import re
import warnings
import psycopg2
from psycopg2 import sql

# Suppress warnings
warnings.filterwarnings("ignore", category=pd.errors.SettingWithCopyWarning)

# Path to the CSV file
file_path = r"/app/generated_users.csv"

# Reading the CSV file
try:
    data = pd.read_csv(file_path)
except FileNotFoundError:
    print("Error: File not found. Ensure 'your_file.csv' exists.")
    data = None
if data is None:
    raise ValueError("The variable 'data' is not initialized. Check the data loading step.")

#Data transformation
if data is not None and 'signup_date' in data.columns:
    data['signup_date'] = pd.to_datetime(data['signup_date'], errors='coerce').dt.strftime('%Y-%m-%d')
    print("Signup dates converted successfully!")
else:
    print("Error: 'signup_date' column is missing or data is None.")


# Filter out records where the `email` field does not contain a valid email address.
def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(email_regex, str(email)))

# Filter out invalid email addresses
data['email'] = data['email'].astype(str)  # Ensure email field is a string
data = data[data['email'].apply(is_valid_email)]

# Add a new column `domain` to the dataset, which should contain the domain name extracted from the `email` address (e.g., for `user@example.com`, the domain would be `example.com`).
data['domain'] = data['email'].str.extract(r'@([\w.-]+)')

# Data loading
# PostgreSQL connection details
db_config = {
    "dbname": "inforce_task",#enter your db
    "user": "postgres",#enter your user
    "password": "your_password",# enter your password
    "host": "postgres", 
    "port": 5432,
}

# Table schema definition
table_name = "generated_users"
columns = {
    "user_id": "Integer",
    "name": "Text",
    "email": "Text",
    "signup_date": "Date",
    "domain": "Text",
}

# Connect to PostgreSQL
conn = None  
cursor = None  
try:
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()

    # Create database table if not exists
    create_table_query = sql.SQL(
        """
        CREATE TABLE IF NOT EXISTS {table} (
            {columns}
        );
        """
    ).format(
        table=sql.Identifier(table_name),
        columns=sql.SQL(", ").join(
            sql.SQL(f"{col} {dtype}") for col, dtype in columns.items()
        ),
    )
    cursor.execute(create_table_query)
    conn.commit()

    # Truncate table to delete previous data
    truncate_query = sql.SQL(
        """
        TRUNCATE TABLE {table};
        """
    ).format(table=sql.Identifier(table_name))
    cursor.execute(truncate_query)
    conn.commit()

    # Insert data into the table
    insert_query = sql.SQL(
        """
        INSERT INTO {table} (user_id, name, email, signup_date, domain)
        VALUES (%s, %s, %s, %s, %s);
        """
    ).format(table=sql.Identifier(table_name))

    for _, row in data.iterrows():
        try:
            cursor.execute(
                insert_query,
                (row['user_id'], row['name'], row['email'], row['signup_date'], row['domain']),
            )
        except Exception as e:
            print(f"Error inserting row: {e}")

    conn.commit()
    print("Data inserted successfully!")

except Exception as e:
    print(f"Error: {e}")
finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()

# Save the transformed data to a CSV file
data.to_csv(r"/app/generated_users_transformed.csv", index=False)

# Execute all queries
def execute_sql_script(file_path, connection, output_csv_path=None):
    with open(file_path, 'r') as file:
        sql_script = file.read()

    with connection.cursor() as cursor:
        cursor.execute(sql_script)
        if cursor.description: 
            results = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]

            # Save results to a CSV file if an output path is provided
            if output_csv_path:
                df = pd.DataFrame(results, columns=column_names)
                df.to_csv(output_csv_path, index=False)
                print(f"Results saved to {output_csv_path}")
            return results
        else:
            print(f"No results for script: {file_path}")
        connection.commit()

# Connect to the database
connection = None
try:
    connection = psycopg2.connect(**db_config)

    # List of SQL scripts and corresponding output file paths
    sql_scripts = [
        ("/app/Query1.sql", "/app/Query1_results.csv"),
        ("/app/Query2.sql", "/app/Query2_results.csv"),
        ("/app/Query3.sql", "/app/Query3_results.csv"),
        ("/app/Query4.sql", "/app/Query4_results.csv"),
        ("/app/Query5.sql", "/app/Query5_results.csv"),
    ]

    # Execute each script and save results
    for script, output_csv in sql_scripts:
        print(f"Executing {script}...")
        execute_sql_script(script, connection, output_csv)

    print("All SQL scripts executed successfully and results saved!")

except Exception as e:
    print(f"Error: {e}")

finally:
    if connection:
        connection.close()