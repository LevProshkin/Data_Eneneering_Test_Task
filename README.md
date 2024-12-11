# Data Engineering Test Task

## How to Build and Run the Docker Containers

### Prerequisites
Ensure you have the following tools installed on your machine:
- Docker
- Docker Compose

### Steps
1. **Clone the Repository**
   Clone the repository to your local machine.

2. **Update Database Parameters**
   - Modify the database credentials in the following files:
     - `Dockerfile`: Update parameters on **line 19**.
     - `docker-compose.yml`: Update parameters on **lines 10 and 27**.
    - Add the following content to a new `.env` file(put your own credentials):
        ```env
        POSTGRES_USER=postgres
        POSTGRES_PASSWORD=your_password
        POSTGRES_DB=inforce_task
        POSTGRES_HOST=postgres
        POSTGRES_PORT=5432

3. **Build and Run Containers**
   - Use the following command in your terminal to build and run the containers:
     ```bash
     docker-compose up -d
     ```
   - This will build and start the containers in detached mode.

---

## Database Schema and Queries

### Schema Design
**Table: `generated_users`**

| Column      | Data Type | Description                                |
|-------------|-----------|--------------------------------------------|
| `user_id`   | Integer   | Unique identifier for each user            |
| `name`      | Text      | Name of the user                           |
| `email`     | Text      | Email address of the user                  |
| `signup_date` | Date     | Date when the user signed up               |
| `domain`    | Text      | Extracted domain from the email address    |

---

### Queries

1. **Create Table**
   ```sql
   CREATE TABLE IF NOT EXISTS generated_users (
       user_id INTEGER,
       name TEXT,
       email TEXT,
       signup_date DATE,
       domain TEXT
   );
   ```

2. **Insert Data**
   ```sql
   INSERT INTO generated_users (user_id, name, email, signup_date, domain)
   VALUES (%s, %s, %s, %s, %s);
   ```

3. **Daily Signup Count**
   ```sql
   SELECT
       DATE(signup_date) AS signup_day,
       COUNT(*) AS user_count
   FROM
       generated_users
   GROUP BY
       signup_day
   ORDER BY
       signup_day;
   ```

4. **Unique Email Domains**
   ```sql
   SELECT DISTINCT
       SPLIT_PART(email, '@', 2) AS email_domain
   FROM
       generated_users
   ORDER BY
       email_domain;
   ```

5. **Recent Signups (Last 7 Days)**
   ```sql
   SELECT *
   FROM
       generated_users
   WHERE
       signup_date >= CURRENT_DATE - INTERVAL '7 days'
   ORDER BY
       signup_date DESC;
   ```

6. **Users from Most Common Domain**
   ```sql
   SELECT *
   FROM
       generated_users
   WHERE
       domain =
       (
           SELECT domain
           FROM generated_users
           GROUP BY domain
           HAVING COUNT(domain) =
           (
               SELECT COUNT(domain)
               FROM generated_users
               GROUP BY domain
               ORDER BY COUNT(domain) DESC
               LIMIT 1
           )
       );
   ```

7. **Delete Unwanted Domains**
   ```sql
   DELETE FROM
       generated_users
   WHERE
       SPLIT_PART(email, '@', 2) NOT IN ('gmail.com', 'yahoo.com', 'example.com');

   SELECT * FROM generated_users;
   ```

---

## Verifying Results

1. **Set Database Credentials**
   - Ensure the database credentials are correctly set in the files mentioned earlier.

2. **Check Logs and Files**
   - Use Docker Desktop or the terminal to verify logs and generated files.

3. **Commands for Verification**
   - To check logs in the terminal:
     ```bash
     docker logs app_container
     ```
   - To view the transformed CSV file within the container:
     ```bash
     docker exec -it app_container cat /app/generated_users_transformed.csv
     ```
   - To copy the transformed CSV file to the host machine:
     ```bash
     docker cp app_container:/app/generated_users_transformed.csv ./generated_users_transformed.csv
     ```

---

## Assumptions

1. **Database Configuration**
   - It is assumed that the user has access to a database and can configure the credentials.

2. **Email Domain Extraction**
   - The domain is extracted using the `SPLIT_PART` function. Ensure the database supports this function or replace it with an equivalent.

3. **Docker Knowledge**
   - Basic knowledge of Docker and Docker Compose is assumed.

4. **Data Availability**
   - Data should be pre-populated or dynamically generated for the queries to return meaningful results.

5. **File Persistence**
   - Files generated inside the container (e.g., transformed CSV) must be manually copied to the host machine if needed.

---

### Notes
- Ensure all dependencies are installed before running the scripts.
- The container will continue running until manually stopped using the `docker stop` command.

