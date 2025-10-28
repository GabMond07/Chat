class MessageDTO:
    def __init__(self, content, user_id):
        self.content = content
        self.user_id = user_id
        
    def to_dict(self):
        return {
            "content": self.content,
            "user_id": self.user_id
        }