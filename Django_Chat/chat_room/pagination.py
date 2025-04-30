from rest_framework.pagination import CursorPagination

class MessageCursorPagination(CursorPagination):
    page_size = 35
    ordering = '-timestamp'
    
    
class ChatCursorPagination(CursorPagination):
    page_size = 35
    ordering = '-last_message'