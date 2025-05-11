# Use an official Python image
FROM python:alpine@sha256:452682e4648deafe431ad2f2391d726d7c52f0ff291be8bd4074b10379bb89ff AS builder

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