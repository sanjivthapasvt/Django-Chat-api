#!/bin/sh
cd Django_Chat/
python manage.py makemigrations chat_room user_api
python manage.py migrate
uvicorn Django_Chat.asgi:application --host 0.0.0.0 --port 8000