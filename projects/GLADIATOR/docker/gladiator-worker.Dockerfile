FROM python:3.11-slim

# Install PostgreSQL client and dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir psycopg2-binary

# Create app directory
WORKDIR /app

# Copy worker script
COPY ../scripts/gladiator_worker.py /app/

# Run worker
CMD ["python", "-u", "gladiator_worker.py"]

