from typing import Optional
from dtos import MessageDTO, ResponseDTO, ConversationDTO
from services.agnostic.entity.conversation_service import ConversationService
from services.agnostic.entity.message_service import MessageService
from services.agnostic.entity.user_service import UserService
from services.agnostic.utility.text_utils import TextUtils
from services.ai_service import AIService
from config import Config

class MessagingCapability:
    """
    Task Service: Gestión de conversaciones
    Combina varios servicios de entidad y utilidad para operaciones de negocio
    """
    
    def __init__(self, ai_service: AIService):
        """
        Inicializa el servicio de mensajería
        
        Args:
            ai_service: Instancia del servicio de IA
        """
        self.ai_service = ai_service
    
    def process_user_message(self, user_id: int, session_id: int, 
                            message_content: str) -> ResponseDTO:
        """
        Procesa un mensaje del usuario (flujo completo)
        
        Este método orquesta:
        1. Validación del usuario
        2. Validación de la entrada
        3. Consulta a IA
        4. Guardar conversación
        5. Devolver respuesta
        
        Args:
            user_id: ID del usuario
            session_id: ID de la sesión
            message_content: Contenido del mensaje
        
        Returns:
            ResponseDTO con el resultado del procesamiento
        """
        # Paso 1: Validar usuario
        user = UserService.get_user(user_id)
        if not user:
            return ResponseDTO.error_response(
                "Usuario no encontrado",
                error_code="USER_NOT_FOUND"
            )
        
        if not user.is_active:
            return ResponseDTO.error_response(
                "Usuario inactivo",
                error_code="USER_INACTIVE"
            )
        
        # Paso 2: Validar entrada
        validation_result = self._validate_input(message_content)
        if not validation_result['valid']:
            return ResponseDTO.error_response(
                validation_result['error'],
                error_code="INVALID_INPUT"
            )
        
        # Limpiar texto
        cleaned_message = TextUtils.sanitize_input(message_content)
        
        # Paso 3: Guardar mensaje del usuario
        user_message = ConversationService.save_conversation_message(
            session_id, 'user', cleaned_message
        )
        
        if not user_message:
            return ResponseDTO.error_response(
                "Error al guardar mensaje",
                error_code="SAVE_ERROR"
            )
        
        # Paso 4: Consultar IA
        ai_response = self._query_ai(cleaned_message)
        if not ai_response:
            return ResponseDTO.error_response(
                "Error al generar respuesta de IA",
                error_code="AI_ERROR"
            )
        
        # Paso 5: Guardar respuesta del bot
        bot_message = ConversationService.save_conversation_message(
            session_id, 'bot', ai_response
        )
        
        if not bot_message:
            return ResponseDTO.error_response(
                "Error al guardar respuesta",
                error_code="SAVE_ERROR"
            )
        
        # Paso 6: Devolver respuesta
        return ResponseDTO.success_response(
            "Mensaje procesado exitosamente",
            data={
                'user_message': user_message.to_dict(),
                'bot_message': bot_message.to_dict()
            }
        )
    
    def create_new_conversation(self, user_id: int, title: str = "Nueva Conversación") -> ResponseDTO:
        """
        Crea una nueva conversación para el usuario
        
        Args:
            user_id: ID del usuario
            title: Título de la conversación
        
        Returns:
            ResponseDTO con la conversación creada
        """
        # Validar usuario
        user = UserService.get_user(user_id)
        if not user:
            return ResponseDTO.error_response(
                "Usuario no encontrado",
                error_code="USER_NOT_FOUND"
            )
        
        # Crear conversación
        conversation_data = ConversationDTO(
            user_id=user_id,
            title=title,
            is_active=True
        )
        
        new_conversation = ConversationService.create_conversation(conversation_data)
        
        if not new_conversation:
            return ResponseDTO.error_response(
                "Error al crear conversación",
                error_code="CREATE_ERROR"
            )
        
        return ResponseDTO.success_response(
            "Conversación creada exitosamente",
            data=new_conversation
        )
    
    def get_conversation_history(self, user_id: int, session_id: int) -> ResponseDTO:
        """
        Obtiene el historial de una conversación
        
        Args:
            user_id: ID del usuario
            session_id: ID de la sesión
        
        Returns:
            ResponseDTO con el historial
        """
        # Validar usuario
        user = UserService.get_user(user_id)
        if not user:
            return ResponseDTO.error_response(
                "Usuario no encontrado",
                error_code="USER_NOT_FOUND"
            )
        
        # Obtener conversación
        conversation = ConversationService.get_conversation(session_id, include_messages=True)
        
        if not conversation:
            return ResponseDTO.error_response(
                "Conversación no encontrada",
                error_code="CONVERSATION_NOT_FOUND"
            )
        
        # Verificar que la conversación pertenece al usuario
        if conversation.user_id != user_id:
            return ResponseDTO.error_response(
                "No autorizado",
                error_code="UNAUTHORIZED"
            )
        
        return ResponseDTO.success_response(
            "Historial obtenido exitosamente",
            data=conversation
        )
    
    def get_user_conversations(self, user_id: int) -> ResponseDTO:
        """
        Obtiene todas las conversaciones de un usuario
        
        Args:
            user_id: ID del usuario
        
        Returns:
            ResponseDTO con lista de conversaciones
        """
        # Validar usuario
        user = UserService.get_user(user_id)
        if not user:
            return ResponseDTO.error_response(
                "Usuario no encontrado",
                error_code="USER_NOT_FOUND"
            )
        
        # Obtener conversaciones
        conversations = ConversationService.get_conversations_by_user(user_id)
        
        return ResponseDTO.success_response(
            "Conversaciones obtenidas exitosamente",
            data=[conv.to_dict() for conv in conversations]
        )
    
    def _validate_input(self, text: str) -> dict:
        """
        Valida la entrada del usuario
        
        Args:
            text: Texto a validar
        
        Returns:
            Diccionario con resultado de validación
        """
        # Verificar longitud
        is_valid, error_msg = TextUtils.validate_length(
            text, 
            Config.MIN_MESSAGE_LENGTH, 
            Config.MAX_MESSAGE_LENGTH
        )
        
        if not is_valid:
            return {'valid': False, 'error': error_msg}
        
        # Verificar contenido ofensivo
        if TextUtils.contains_offensive_content(text):
            return {'valid': False, 'error': 'El mensaje contiene contenido no permitido'}
        
        return {'valid': True, 'error': None}
    
    def _query_ai(self, text: str) -> Optional[str]:
        """
        Consulta al servicio de IA
        
        Args:
            text: Texto de entrada
        
        Returns:
            Respuesta generada por la IA
        """
        if not self.ai_service.is_ready():
            return "Lo siento, el servicio de IA no está disponible en este momento."
        
        response = self.ai_service.query_ai_model(
            text,
            max_length=Config.AI_MAX_LENGTH
        )
        
        if not response:
            return "Lo siento, no pude generar una respuesta en este momento."
        
        return response