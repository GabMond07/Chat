from models.chat_message import ChatMessage
from models import db
from typing import Optional, List

class MessageService:
    @staticmethod
    def save_message(session_id: int, user_id: int, content: str, is_bot: bool = False) -> Optional[ChatMessage]:
        """
        Guarda un nuevo mensaje en la base de datos
        
        Args:
            session_id: ID de la sesión/conversación
            user_id: ID del usuario que envía el mensaje
            content: Contenido del mensaje
            is_bot: Si el mensaje es del bot o del usuario
            
        Returns:
            ChatMessage object if successful, None otherwise
        """
        try:
            message = ChatMessage(
                session_id=session_id,
                user_id=user_id,
                content=content,
                is_bot=is_bot
            )
            
            db.session.add(message)
            db.session.commit()
            
            return message
            
        except Exception as e:
            print(f"Error saving message: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def get_messages(session_id: int) -> List[ChatMessage]:
        """
        Obtiene todos los mensajes de una conversación
        
        Args:
            session_id: ID de la sesión/conversación
            
        Returns:
            List of ChatMessage objects
        """
        try:
            return ChatMessage.query.filter_by(session_id=session_id).order_by(ChatMessage.created_at.asc()).all()
        except Exception as e:
            print(f"Error getting messages: {str(e)}")
            return []