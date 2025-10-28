from datetime import datetime
from models import db
from models.chat_message import ChatMessage

class Session(db.Model):
    __tablename__ = 'sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False, default="Nueva Conversación")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relaciones
    messages = db.relationship(ChatMessage, backref='session', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'created_at': self.created_at.isoformat(),
            'messages': [message.to_dict() for message in self.messages]
        }