#Python image
FROM python:3.13-slim

# environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt
# Copy the project files
COPY . .

#for migration and runserver command
RUN chmod +x /app/entrypoint.sh
# Expose port for django server
EXPOSE 8000

ENTRYPOINT [ "/app/entrypoint.sh" ]