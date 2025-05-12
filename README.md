# 💬 Django Chat API

A powerful, scalable chat backend built using **Django** and **Django REST Framework**, supporting **private messaging**, **group chats**, **notifications**, **typing indicators**, **read receipts**, **admin roles**, and much more.

> 🚧 Currently under active development!

---

## ✨ Features

### User Chats

- 1-to-1 private chats
- Group chats with multiple participants
- Message read status
- Typing indicators

### Groups

- Create and manage group chats
- Add/remove participants
- Assign admins within groups
- Group image support
- Shareable group/room ID

### Messages

- Text messaging
- Image support
- Search through messages
- Read/unread message tracking
- Last message preview in room

### Notifications

- In-app notifications
- Notification history stored in the database
- Mark notifications as read
- Receive updates when new messages arrive
- **Push Notifications** (coming soon)

### User Management

- Register/login/logout
- Add/remove friends
- Friend request system
- Custom user profiles
- Admin-only permissions for certain actions

---

## 🛠️ Tech Stack

- **Backend:** Django, Django REST Framework
- **Authentication:** JWT Authentication
- **Database:** PostgreSQL (recommended), Redis for caching
- **Realtime:** WebSocket via Django Channels
- **Frontend:** To be built (React frontend in progress)

---

## 📦 API Endpoints

### 🔹 **Chat Rooms**

- `GET /api/chatrooms/` — List all chat rooms with pagination
- `POST /api/chatrooms/` — Create a new chat room
- `GET /api/chatrooms/{id}/` — Retrieve a specific chat room
- `PUT /api/chatrooms/{id}/` — Update a chat room
- `PATCH /api/chatrooms/{id}/` — Partially update a chat room
- `DELETE /api/chatrooms/{id}/` — Delete a chat room
- `POST /api/chatrooms/{id}/add_members/` — Add members to a chat room
- `POST /api/chatrooms/{id}/assign_admin/` — Assign an admin in the chat room
- `POST /api/chatrooms/{id}/leave_room/` — Leave a chat room
- `GET /api/chatrooms/{id}/participants/` — Get list of participants
- `POST /api/chatrooms/{id}/remove_member/` — Remove a member
- `GET /api/chatrooms/{id}/shareable_link/` — Get shareable invite link

### 🔹 **Messages**

- `GET /api/chatrooms/{chatroom_pk}/messages/` — List all messages in a chat room with pagination
- `POST /api/chatrooms/{chatroom_pk}/messages/` — Send a new message
- `GET /api/chatrooms/{chatroom_pk}/messages/{id}/` — Retrieve a specific message
- `PUT /api/chatrooms/{chatroom_pk}/messages/{id}/` — Update a message
- `PATCH /api/chatrooms/{chatroom_pk}/messages/{id}/` — Partially update a message
- `DELETE /api/chatrooms/{chatroom_pk}/messages/{id}/` — Delete a message
- `POST /api/chatrooms/{chatroom_pk}/messages/{id}/mark_as_read/` — Mark a message as read
- `GET /api/chatrooms/{chatroom_pk}/messages/{id}/message_read_status/` — Get read status of a message

### 🔹 **Authentication**

- `POST /api/register/` — Register a new user
- `POST /api/login/` — Log in a user
- `POST /api/logout/` — Log out current user
- `POST /api/token/refresh/` — Refresh authentication token

### 🔹 **User Profile**

- `GET /api/profile/` — Retrieve user profile
- `PUT /api/profile/` — Update user profile
- `PATCH /api/profile/` — Partially update profile

### 🔹 **Users**

- `GET /api/users/` — List all users
- `GET /api/users/{id}/` — Retrieve a specific user

### 🔹 **Friends & Friend Requests**

- `GET /api/friend-requests/` — List all friend requests
- `POST /api/friend-requests/` — Send a friend request
- `GET /api/friend-requests/{id}/` — Retrieve a specific friend request
- `POST /api/friend-requests/{id}/accept/` — Accept a friend request
- `POST /api/friend-requests/{id}/cancel/` — Cancel a friend request
- `POST /api/friend-requests/{id}/reject/` — Reject a friend request
- `GET /api/friends/list_friends/` — List all friends
- `GET /api/friends/{id}/` — Retrieve a specific friend
- `POST /api/friends/{id}/remove_friend/` — Remove a friend

### 🔹 **Notifications**

- `GET /api/notifications/` — List all notifications
- `POST /api/notifications/` — Create a notification
- `GET /api/notifications/{id}/` — Retrieve a specific notification
- `PUT /api/notifications/{id}/` — Update a notification
- `PATCH /api/notifications/{id}/` — Partially update a notification
- `DELETE /api/notifications/{id}/` — Delete a notification
- `POST /api/notifications/{id}/mark_read/` — Mark a notification as read
- `POST /api/notifications/mark_all_read/` — Mark all notifications as read
- `GET /api/notifications/unread/` — Get unread notifications

### 🔹 **Misc**

- `GET /api/schema/` — API schema definition

---

## 🔌 WebSocket Endpoints

These WebSocket routes enable real-time functionality:

### 1. **Chat Room WebSocket**

- **Endpoint:** `ws/chat/<chatroom_id>/?token=<access_token>`
- **Description:** Allows users to join a specific chat room and receive real-time updates for new messages, typing indicators, and more.
- **Example:**  
  `ws://localhost:8000/ws/chat/123/?token=<access_token>`

### 2. **ChatRoom Sidebar WebSocket**

- **Endpoint:** `ws/sidebar/?token=<access_token>`
- **Description:** Enables real-time updates for the user's chat list (sidebar). It dynamically reflects:

  - New incoming messages
  - Live chat switching updates
  - Reordering of chats based on recent activity

  This WebSocket ensures the sidebar always displays the most current state of all conversations.

- **Example:**  
  `ws://localhost:8000/ws/sidebar/?token=<access_token>`

### 3. **Notification WebSocket**

- **Endpoint:** `ws/notifications/?token=<access_token>`
- **Description:** Receives real-time notifications about various events (e.g., new messages, friend requests).
- **Example:**  
  `ws://localhost:8000/ws/notifications/?token=<access_token>`

---

## 🚧 Coming Soon

- [ ] Video/Voice calling via WebRTC
- [ ] [Web frontend](https://github.com/sanjivthapasvt/Chatapp-frontend)

---

## 🚀 Getting Started

1. **Clone the repository**:

```bash
git clone https://github.com/sanjivthapasvt/Django-Chat-api.git
cd Django-Chat-api
```

2. Setup Virtual env and Install dependencies:

```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
```

3. Create a .env file in the root directory with the following contents(change based on your setup):

```bash
   # Django secret key
   SECRET_KEY=your-secret-key-here

   # Allowed hosts for Django (comma-separated for multiple hosts)
   DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

   # PostgreSQL database connection string
   # Format: postgresql://<username>:<password>@<host>:<port>/<database_name>
   DATABASE_URL=postgresql://your-username:your-password@localhost:5432/your-database-name

   # Redis connection string (for caching and WebSockets)
   # Format: redis://<host>:<port>
   REDIS_URL=redis://localhost:6379

   # CSRF allowed origins (comma-separated if multiple)
   CSRF_ALLOWED=http://localhost:8000

```

4. Apply migrations:

```bash
   cd Django_Chat && python manage.py migrate
```

5. Create a superuser if you want:

```bash
   python manage.py createsuperuser
```

6. Run the server:

```bash
   python manage.py runserver
```

7. Access the API:  
   http://localhost:8000/api/

8. Access the API schema:  
   http://127.0.0.1:8000/api/schema/

## 🧪 Testing

Use the API schema to explore and test all endpoints.

## 📄 License

Feel free to fork and improve this project.
