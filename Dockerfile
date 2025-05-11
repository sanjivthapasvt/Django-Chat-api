#Python image
FROM python:3.13-slim

# environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 

# Set working directory
WORKDIR /app

RUN apt-get update && apt-get install -y build-essential libpq-dev

# Install dependencies
COPY Django_Chat/requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt
# Copy the project files
COPY Django_Chat /app/
COPY /entrypoint.sh /app/
#for migration and runserver command
RUN chmod +x /app/entrypoint.sh
# Expose port for django server
EXPOSE 8000

ENTRYPOINT [ "/app/entrypoint.sh" ]