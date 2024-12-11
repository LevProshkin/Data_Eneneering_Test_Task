import os
import pandas as pd
import re
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

class DataPipeline:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.data = None
        self.db_config = {
            "user": os.getenv("POSTGRES_USER"),
            "password": os.getenv("POSTGRES_PASSWORD"),
            "dbname": os.getenv("POSTGRES_DB"),
            "host": os.getenv("POSTGRES_HOST"),
            "port": os.getenv("POSTGRES_PORT"),
        }

    def load_data(self):
        try:
            self.data = pd.read_csv(self.csv_path)
            print("Data loaded successfully!")
        except FileNotFoundError:
            raise FileNotFoundError("Error: File not found. Ensure the CSV file exists.")

    def transform_data(self):
        if self.data is None:
            raise ValueError("Data not loaded. Call load_data() first.")

        # Convert signup_date to 'YYYY-MM-DD'
        if 'signup_date' in self.data.columns:
            self.data['signup_date'] = pd.to_datetime(self.data['signup_date'], errors='coerce').dt.strftime('%Y-%m-%d')
            print("Signup dates converted successfully!")
        else:
            print("Warning: 'signup_date' column is missing.")

        # Filter out invalid email addresses
        def is_valid_email(email):
            email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
            return bool(re.match(email_regex, str(email)))

        self.data['email'] = self.data['email'].astype(str)
        self.data = self.data[self.data['email'].apply(is_valid_email)]

        # Add domain column
        self.data['domain'] = self.data['email'].str.extract(r'@([\w.-]+)')
        print("Data transformation completed!")

    def save_transformed_data(self, output_path):
        if self.data is not None:
            self.data.to_csv(output_path, index=False)
            print(f"Transformed data saved to {output_path}")
        else:
            raise ValueError("No data to save. Run transform_data() first.")

    def load_to_database(self, table_name, table_schema):
        if self.data is None:
            raise ValueError("Data not loaded or transformed. Run transform_data() first.")

        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()

            # Create table if not exists
            create_table_query = sql.SQL(
                """
                CREATE TABLE IF NOT EXISTS {table} (
                    {columns}
                );
                """
            ).format(
                table=sql.Identifier(table_name),
                columns=sql.SQL(", ").join(
                    sql.SQL(f"{col} {dtype}") for col, dtype in table_schema.items()
                ),
            )
            cursor.execute(create_table_query)
            conn.commit()

            # Truncate table
            cursor.execute(sql.SQL("TRUNCATE TABLE {table};").format(table=sql.Identifier(table_name)))
            conn.commit()

            # Insert data
            insert_query = sql.SQL(
                """
                INSERT INTO {table} ({columns})
                VALUES ({placeholders});
                """
            ).format(
                table=sql.Identifier(table_name),
                columns=sql.SQL(", ").join(map(sql.Identifier, self.data.columns)),
                placeholders=sql.SQL(", ").join(sql.Placeholder() for _ in self.data.columns),
            )

            for _, row in self.data.iterrows():
                cursor.execute(insert_query, tuple(row))

            conn.commit()
            print("Data inserted into database successfully!")

        except Exception as e:
            print(f"Error: {e}")

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def execute_sql_scripts(self, scripts):
        conn = None
        try:
            conn = psycopg2.connect(**self.db_config)
            for script_path, output_path in scripts:
                with open(script_path, 'r') as file:
                    script = file.read()
                with conn.cursor() as cursor:
                    cursor.execute(script)
                    if cursor.description:  # If the script produces a result
                        results = cursor.fetchall()
                        column_names = [desc[0] for desc in cursor.description]
                        df = pd.DataFrame(results, columns=column_names)
                        df.to_csv(output_path, index=False)
                        print(f"Results of {script_path} saved to {output_path}")
                    conn.commit()
        except Exception as e:
            print(f"Error executing SQL scripts: {e}")
        finally:
            if conn:
                conn.close()

if __name__ == "__main__":
    # Initialize pipeline
    pipeline = DataPipeline(csv_path="/app/generated_users.csv")

    # Load and transform data
    pipeline.load_data()
    pipeline.transform_data()

    # Save transformed data
    pipeline.save_transformed_data(output_path="/app/generated_users_transformed.csv")

    # Load to database
    table_name = "generated_users"
    table_schema = {
        "user_id": "Integer",
        "name": "Text",
        "email": "Text",
        "signup_date": "Date",
        "domain": "Text",
    }
    pipeline.load_to_database(table_name, table_schema)

    # Execute additional SQL scripts
    sql_scripts = [
        ("/app/Query1.sql", "/app/Query1_results.csv"),
        ("/app/Query2.sql", "/app/Query2_results.csv"),
        ("/app/Query3.sql", "/app/Query3_results.csv"),
        ("/app/Query4.sql", "/app/Query4_results.csv"),
        ("/app/Query5.sql", "/app/Query5_results.csv"),
    ]
    pipeline.execute_sql_scripts(sql_scripts)