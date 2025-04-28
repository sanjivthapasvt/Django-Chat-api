# Use an official Python image
FROM python:alpine@sha256:18159b2be11db91f84b8f8f655cd860f805dbd9e49a583ddaac8ab39bf4fe1a7 AS builder

# environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
# Copy the project files
COPY . .

#for migration and runserver command
RUN chmod +x /app/entrypoint.sh
# Expose port for django server
EXPOSE 8000

ENTRYPOINT [ "/app/entrypoint.sh" ]