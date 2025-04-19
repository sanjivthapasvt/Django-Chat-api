
# 🗨️ Django Chat API

A powerful, scalable chat backend built using **Django** and **Django REST Framework**, supporting **private messaging**, **group chats**, **notifications**, **typing indicators**, **read receipts**, **admin roles**, and much more.

> 🚧 Currently under active development!

## ✨ Features

- **User Chats**
  - 1-to-1 private chats
  - Group chats with multiple participants
  - Message read status and typing indicators

- **Groups**
  - Create and manage group chats
  - Add/remove participants
  - Assign admins within groups
  - Group image support
  - Shareable group/room ID

- **Messages**
  - Text messaging
  - Search through messages (planned)
  - Track read/unread messages
  - Last message preview in room

- **Notifications**
  - Receive updates when new messages arrive (in progress)

- **User Management**
  - Register/login/logout
  - Custom user profiles
  - Admin-only permissions for certain actions

## 🧱 Tech Stack

- **Backend:** Django, Django REST Framework
- **Authentication:** Token-based
- **Database:** PostgreSQL (recommended)
- **Realtime:** WebSockets integration coming soon
- **Frontend:** To be built (React/Android app coming soon)

## 📦 API Endpoints

### 🔹 Chat Rooms

- `GET /api/chatrooms/` — List all chat rooms
- `POST /api/chatrooms/` — Create a new chat room
- `GET /api/chatrooms/{id}/` — Retrieve a specific chat room
- `PUT /api/chatrooms/{id}/` — Update a chat room
- `PATCH /api/chatrooms/{id}/` — Partially update a chat room
- `DELETE /api/chatrooms/{id}/` — Delete a chat room
- `POST /api/chatrooms/{id}/add_members/` — Add members to a chat room
- `POST /api/chatrooms/{id}/assign_admin/` — Assign an admin in the chat room
- `GET /api/chatrooms/{id}/participants/` — Get list of participants
- `POST /api/chatrooms/{id}/remove_member/` — Remove a member
- `GET /api/chatrooms/{id}/shareable_link/` — Get shareable invite link

### 🔹 Authentication

- `POST /api/register/` — Register a new user
- `POST /api/login/` — Log in a user
- `POST /api/logout/` — Log out current user

### 🔹 User Profile

- `GET /api/profile/` — Retrieve user profile
- `PUT /api/profile/` — Update user profile
- `PATCH /api/profile/` — Partially update profile

### 🔹 Misc

- `GET /api/schema/` — API schema definition
- `GET /api/schema/swagger-ui/` — Interactive Swagger UI

## 🚧 Coming Soon

- [ ] Video/Voice calling via WebRTC
- [ ] Realtime chat with Django Channels
- [ ] Android and Web frontend
- [ ] File/image sharing support
- [ ] End-to-end encryption
- [ ] Message search
- [ ] Read receipts & typing indicators

## 🚀 Getting Started

1. Clone this repo:
   ```bash
   git clone https://github.com/sanjivthapasvt/Django-Chat-api.git
   cd Django-Chat-api
   ```

2. Setup Virtual env and Install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Apply migrations:
   ```bash
   cd Django_Chat && python manage.py migrate
   ```

4. Create a superuser if you want:
   ```bash
   python manage.py createsuperuser
   ```

5. Run the server:
   ```bash
   python manage.py runserver
   ```

6. Access the API:  
   `http://localhost:8000/api/`

7. Access the Swagger UI:  
   `http://127.0.0.1:8000/api/schema/swagger-ui/`

## 🧪 Testing

Use the Swagger/OpenAPI docs to interactively test all endpoints.

## 📄 License

Feel free to fork and improve this project. MIT Licensed.
