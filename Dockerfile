# Use Python 3.12.5 as the base image
FROM python:3.12.5

# Set the working directory inside the container
WORKDIR /app

# Copy the dataset into the container
COPY generated_users.csv /app/

# Copy the Python dependencies file into the container
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files into the container
COPY . /app/

# Set environment variables for PostgreSQL
ENV POSTGRES_HOST=postgres
ENV POSTGRES_PORT=5432
#enter your user
ENV POSTGRES_USER=postgres
#enter your password
ENV POSTGRES_PASSWORD=your_password 
#enter your db
ENV POSTGRES_DB=inforce_task

# Debugging step to verify files
RUN ls /app

# Run the application
CMD ["bash", "-c", "python /app/generated_users.py && tail -f /dev/null"]