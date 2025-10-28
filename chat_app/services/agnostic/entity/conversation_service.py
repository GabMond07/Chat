from models.session import Session
from models import db
from dtos import ConversationDTO
from services.agnostic.entity.user_service import UserService

class ConversationService:
    @staticmethod
    def create_conversation(user_id: int, title: str = "Nueva Conversación") -> Session:
        """
        Crea una nueva conversación para un usuario
        
        Args:
            user_id: ID del usuario
            title: Título de la conversación
            
        Returns:
            Session object if successful, None otherwise
        """
        try:
            # Verificar que el usuario existe
            user = UserService.get_user(user_id)
            if not user:
                return None
                
            # Crear nueva sesión
            session = Session(
                user_id=user_id,
                title=title
            )
            
            db.session.add(session)
            db.session.commit()
            
            return session
            
        except Exception as e:
            print(f"Error creating conversation: {str(e)}")
            db.session.rollback()
            return None
            
    @staticmethod
    def get_conversation(conversation_id: int) -> Session:
        """
        Obtiene una conversación por su ID
        
        Args:
            conversation_id: ID de la conversación
            
        Returns:
            Session object if found, None otherwise
        """
        try:
            return Session.query.get(conversation_id)
        except Exception as e:
            print(f"Error getting conversation: {str(e)}")
            return None
            
    @staticmethod
    def get_user_conversations(user_id: int) -> list:
        """
        Obtiene todas las conversaciones de un usuario
        
        Args:
            user_id: ID del usuario
            
        Returns:
            List of Session objects
        """
        try:
            return Session.query.filter_by(user_id=user_id).all()
        except Exception as e:
            print(f"Error getting user conversations: {str(e)}")
            return []