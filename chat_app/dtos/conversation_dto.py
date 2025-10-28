class ConversationDTO:
    def __init__(self, user_id, title="Nueva Conversación", messages=None):
        self.user_id = user_id
        self.title = title
        self.messages = messages or []
        
    def to_dict(self):
        return {
            "user_id": self.user_id,
            "title": self.title,
            "messages": self.messages
        }