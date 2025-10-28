class ConversationDTO:
    def __init__(self, participants, messages=None):
        self.participants = participants
        self.messages = messages or []
        
    def to_dict(self):
        return {
            "participants": self.participants,
            "messages": self.messages
        }