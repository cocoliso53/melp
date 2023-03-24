# Use the official Python image as the base image
FROM python:3.8-slim-buster

# Set the working directory
WORKDIR /app

# Copy requirements.txt to the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install spatialite
RUN apt-get update && apt-get install -y libsqlite3-mod-spatialite

# Copy the rest of the application code
COPY ./app /app

# Run popscript.py to create and populate the SQLite database
RUN python popscript.py

# Expose the FastAPI port
EXPOSE 80

# Start the FastAPI application
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "80"]
