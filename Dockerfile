# Use a lightweight Python image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install system dependencies and Poetry
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project dependency files
COPY pyproject.toml poetry.lock ./

# Install Python dependencies
RUN pip install --no-cache-dir poetry \
    && poetry install --no-root

# Copy the rest of the application code
COPY src/ ./src/

# Expose the application's port (if applicable)
EXPOSE 8000

# Define the command to run the application
CMD ["poetry", "run", "python", "-m", "app"]
