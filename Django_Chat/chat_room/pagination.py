from rest_framework.pagination import CursorPagination

# For paginating messages (newest first)
class MessageCursorPagination(CursorPagination):
    page_size = 35
    ordering = '-timestamp'

# For paginating chats (most recent activity first)
class ChatCursorPagination(CursorPagination):
    page_size = 35
    ordering = '-last_message'