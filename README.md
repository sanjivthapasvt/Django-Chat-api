
# 💬 Django Chat API

A powerful, scalable chat backend built using **Django** and **Django REST Framework**, supporting **private messaging**, **group chats**, **notifications**, **typing indicators**, **read receipts**, **admin roles**, and much more.

> 🚧 Currently under active development!

## ✨ Features

- **User Chats**
  - 1-to-1 private chats
  - Group chats with multiple participants
  - Message read status
  - Typing indicators

- **Groups**
  - Create and manage group chats
  - Add/remove participants
  - Assign admins within groups
  - Group image support
  - Shareable group/room ID

- **Messages**
  - Text messaging
  - Search through messages
  - Read/unread message tracking
  - Last message preview in room

- **Notifications**
  - In-app notifications
  - Notification history stored in database
  - Receive updates when new messages arrive
  - Push Notifications(soon)

- **User Management**
  - Register/login/logout
  - Add/remove friends
  - See mutual friends
  - Custom user profiles
  - Admin-only permissions for certain actions

## 🛠️ Tech Stack

- **Backend:** Django, Django REST Framework
- **Authentication:** Token-based
- **Database:** PostgreSQL (recommended), redis for caching
- **Realtime:** WebSocket via Django Channels
- **Frontend:** To be built (React currently working on it)

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

### 🔹 Friends

- `POST /api/add-friend/` — Send a friend request
- `GET /api/mutual-friends/` — Get mutual friends
- `GET /api/friend-requests/` — Retrieve all friend requests
- `POST /api/friend-requests/` — Create a friend request
- `GET /api/friend-requests/{id}/` — Retrieve a specific friend request
- `PUT /api/friend-requests/{id}/` — Update a friend request
- `PATCH /api/friend-requests/{id}/` — Partially update a friend request
- `DELETE /api/friend-requests/{id}/` — Delete a friend request
- `POST /api/friend-requests/{id}/accept/` — Accept a friend request
- `POST /api/friend-requests/{id}/cancel/` — Cancel a friend request
- `POST /api/friend-requests/{id}/reject/` — Reject a friend request
- `GET /api/friends/list_friends/` — List all friends
- `GET /api/friends/mutual_friends/{user_id}/` — Get mutual friends with a specific user


### 🔹 Misc

- `GET /api/schema/` — API schema definition
- `GET /api/schema/swagger-ui/` — Interactive Swagger UI

## 🔌 WebSocket Endpoints

These WebSocket routes enable real-time functionality:

1. **Chat Room WebSocket**  
   - **Endpoint:** `ws/chat/<chatroom_id>/`
   - **Description:** This endpoint allows users to join a specific chat room and receive real-time updates for new messages, typing indicators, and more.
   - **Example:**
     ```javascript
     ws://localhost:8000/ws/chat/123/
     ```

2. **Notification WebSocket**  
   - **Endpoint:** `ws/notifications/`
   - **Description:** This WebSocket endpoint allows users to receive real-time notifications about various events (e.g., new messages, friend requests).
   - **Example:**
     ```javascript
     ws://localhost:8000/ws/notifications/
     ```

## 🚧 Coming Soon

- [ ] Video/Voice calling via WebRTC
- [ ] [Web frontend](https://github.com/sanjivthapasvt/Chatapp-frontend)

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
