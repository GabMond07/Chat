class ChatMessage:
    def __init__(self, message_id, user_id, content, timestamp):
        self.message_id = message_id
        self.user_id = user_id
        self.content = content
        self.timestamp = timestamp