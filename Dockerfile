# Base Python image with slimmed-down environment
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies required to build psycopg2 and other packages
RUN apt-get update && \
    apt-get install -y gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Copy the custom entrypoint script and make it executable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose the Flask application port
EXPOSE 5000

# Run the entrypoint script
CMD ["/entrypoint.sh"]
