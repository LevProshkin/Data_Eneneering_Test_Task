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

# Set environment variables (use actual values or `.env` for secrets)
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["bash", "-c", "python /app/generated_users.py && tail -f /dev/null"]