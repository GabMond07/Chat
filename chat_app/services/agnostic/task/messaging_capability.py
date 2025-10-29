from typing import Optional
import traceback
from dtos import MessageDTO, ResponseDTO, ConversationDTO
from services.agnostic.entity.conversation_service import ConversationService
from services.agnostic.entity.message_service import MessageService
from services.agnostic.entity.user_service import UserService
from services.agnostic.utility.text_utils import TextUtils
from services.ai_service import AIService
from config import Config
from utils.logger import logger

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
    
    def process_user_message(self, user_id: int, session_id: int, message_content: str) -> ResponseDTO:
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
        logger.info(f"Iniciando procesamiento de mensaje - User ID: {user_id}, Session ID: {session_id}")
        
        try:
            # Paso 1: Validar usuario
            logger.debug(f"Validando usuario {user_id}")
            user = UserService.get_user(user_id)
        except Exception as e:
            logger.error(f"Error al validar usuario: {str(e)}\n{traceback.format_exc()}")
            return ResponseDTO.error_response(
                "Error al validar usuario",
                error_code="USER_VALIDATION_ERROR"
            )

        if not user:
            logger.warning(f"Usuario no encontrado: {user_id}")
            return ResponseDTO.error_response(
                "Usuario no encontrado",
                error_code="USER_NOT_FOUND"
            )
        
        if not user.is_active:
            logger.warning(f"Usuario inactivo: {user_id}")
            return ResponseDTO.error_response(
                "Usuario inactivo",
                error_code="USER_INACTIVE"
            )
        
        # Paso 2: Validar entrada
        logger.debug("Validando entrada del mensaje")
        validation_result = self._validate_input(message_content)
        if not validation_result['valid']:
            logger.warning(f"Validación fallida: {validation_result['error']}")
            return ResponseDTO.error_response(
                validation_result['error'],
                error_code="INVALID_INPUT"
            )
        
        # Limpiar texto
        logger.debug("Limpiando texto del mensaje")
        cleaned_message = TextUtils.sanitize_input(message_content)
        
        # Paso 3: Validar que la conversación existe
        logger.debug(f"Verificando conversación {session_id}")
        conversation = ConversationService.get_conversation(session_id)
        if not conversation:
            logger.warning(f"Conversación no encontrada: {session_id}")
            return ResponseDTO.error_response(
                "Conversación no encontrada",
                error_code="CONVERSATION_NOT_FOUND"
            )
            
        # Paso 4: Guardar mensaje del usuario
        logger.debug(f"Guardando mensaje del usuario en sesión {session_id}")
        try:
            user_message = MessageService.save_message(
                session_id=session_id,
                user_id=user_id,
                content=cleaned_message,
                is_bot=False
            )
            
            if not user_message:
                logger.error(f"Error al guardar mensaje del usuario - Session ID: {session_id}")
                return ResponseDTO.error_response(
                    "Error al guardar mensaje",
                    error_code="SAVE_ERROR"
                )
        except Exception as e:
            logger.error(f"Excepción al guardar mensaje del usuario: {str(e)}\n{traceback.format_exc()}")
            return ResponseDTO.error_response(
                f"Error al guardar mensaje: {str(e)}",
                error_code="SAVE_ERROR"
            )
        
        # Paso 5: Consultar IA
        logger.debug("Consultando servicio de IA")
        try:
            if not self.ai_service.is_ready():
                logger.error("Servicio de IA no está inicializado")
                # Intentar cargar el modelo si no está listo
                if self.ai_service.load_model():
                    logger.info("Modelo cargado exitosamente en el intento")
                else:
                    logger.error("No se pudo cargar el modelo de IA")
                    return ResponseDTO.error_response(
                        "Servicio de IA no disponible",
                        error_code="AI_SERVICE_ERROR"
                    )
            
            # Consultar al modelo
            ai_response = self.ai_service.query_ai_model(
                cleaned_message,
                max_length=1000
            )
            
            if not ai_response:
                logger.error("Servicio de IA no generó respuesta")
                return ResponseDTO.error_response(
                    "No se pudo generar una respuesta",
                    error_code="AI_GENERATION_ERROR"
                )
                
            logger.info(f"IA generó respuesta: {ai_response[:100]}...")
            
        except Exception as e:
            logger.error(f"Error en el servicio de IA: {str(e)}\n{traceback.format_exc()}")
            return ResponseDTO.error_response(
                "Error al procesar la respuesta",
                error_code="AI_PROCESSING_ERROR"
            )
        
        # Paso 6: Guardar respuesta del bot
        bot_message = MessageService.save_message(
            session_id=session_id,
            user_id=user_id,  # Usamos el mismo user_id para mantener el contexto
            content=ai_response,
            is_bot=True
        )
        
        if not bot_message:
            return ResponseDTO.error_response(
                "Error al guardar respuesta",
                error_code="SAVE_ERROR"
            )
        
        # Paso 7: Devolver respuesta
        logger.info(f"Mensaje procesado exitosamente - Session ID: {session_id}")
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
        logger.info(f"Creando nueva conversación - User ID: {user_id}, Title: {title}")
        
        try:
            # Validar usuario
            user = UserService.get_user(user_id)
            if not user:
                logger.warning(f"Usuario no encontrado: {user_id}")
                return ResponseDTO.error_response(
                    "Usuario no encontrado",
                    error_code="USER_NOT_FOUND"
                )
            
            # Crear conversación
            new_conversation = ConversationService.create_conversation(
                user_id=user_id,
                title=title
            )
            if not new_conversation:
                logger.error(f"Error al crear conversación para usuario {user_id}")
                return ResponseDTO.error_response(
                    "Error al crear conversación",
                    error_code="CREATE_ERROR"
                )
            # Convertir a dict para log y respuesta
            conversation_dict = new_conversation.to_dict() if hasattr(new_conversation, 'to_dict') else {'id': getattr(new_conversation, 'id', 'N/A')}
            logger.info(f"Conversación creada exitosamente - ID: {conversation_dict.get('id', 'N/A')}")
            return ResponseDTO.success_response(
                "Conversación creada exitosamente",
                data=conversation_dict
            )
        except Exception as e:
            logger.error(f"Error inesperado al crear conversación: {str(e)}\n{traceback.format_exc()}")
            return ResponseDTO.error_response(
                f"Error interno: {str(e)}",
                error_code="INTERNAL_ERROR"
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
        logger.info(f"Obteniendo historial - User ID: {user_id}, Session ID: {session_id}")
        
        try:
            # Validar usuario
            logger.debug(f"Validando usuario {user_id}")
            user = UserService.get_user(user_id)
            if not user:
                logger.warning(f"Usuario no encontrado: {user_id}")
                return ResponseDTO.error_response(
                    "Usuario no encontrado",
                    error_code="USER_NOT_FOUND"
                )
            
            # Obtener conversación
            logger.debug(f"Buscando conversación {session_id}")
            try:
                conversation = ConversationService.get_conversation(session_id)
            except Exception as e:
                logger.error(f"Error al obtener conversación: {str(e)}\n{traceback.format_exc()}")
                return ResponseDTO.error_response(
                    f"Error al obtener conversación: {str(e)}",
                    error_code="INTERNAL_ERROR"
                )
            
            if not conversation:
                logger.warning(f"Conversación no encontrada: {session_id}")
                return ResponseDTO.error_response(
                    "Conversación no encontrada",
                    error_code="CONVERSATION_NOT_FOUND"
                )
            
            # Verificar que la conversación pertenece al usuario
            # NOTA: conversation puede ser un dict o un objeto, adaptamos
            conv_user_id = conversation.get('user_id') if isinstance(conversation, dict) else getattr(conversation, 'user_id', None)
            
            if conv_user_id != user_id:
                logger.warning(f"Usuario {user_id} no autorizado para acceder a conversación {session_id}")
                return ResponseDTO.error_response(
                    "No autorizado para acceder a esta conversación",
                    error_code="UNAUTHORIZED"
                )
            
            # Convertir a diccionario para la respuesta
            try:
                if isinstance(conversation, dict):
                    conversation_dict = conversation
                else:
                    conversation_dict = conversation.to_dict()
                
                logger.info(f"Historial obtenido exitosamente para conversación {session_id}")
                return ResponseDTO.success_response(
                    "Historial obtenido exitosamente",
                    data=conversation_dict
                )
            except Exception as e:
                logger.error(f"Error al convertir conversación a diccionario: {str(e)}\n{traceback.format_exc()}")
                return ResponseDTO.error_response(
                    "Error al procesar datos de la conversación",
                    error_code="INTERNAL_ERROR"
                )
                
        except Exception as e:
            logger.error(f"Error inesperado al obtener historial: {str(e)}\n{traceback.format_exc()}")
            return ResponseDTO.error_response(
                "Error interno del servidor",
                error_code="INTERNAL_ERROR"
            )
    
    def get_user_conversations(self, user_id: int) -> ResponseDTO:
        """
        Obtiene todas las conversaciones de un usuario
        
        Args:
            user_id: ID del usuario
        
        Returns:
            ResponseDTO con lista de conversaciones
        """
        logger.info(f"Obteniendo conversaciones del usuario {user_id}")
        
        try:
            # Validar usuario
            user = UserService.get_user(user_id)
            if not user:
                logger.warning(f"Usuario no encontrado: {user_id}")
                return ResponseDTO.error_response(
                    "Usuario no encontrado",
                    error_code="USER_NOT_FOUND"
                )
            
            # Obtener conversaciones
            conversations = ConversationService.get_user_conversations(user_id)
            
            # Convertir a diccionarios
            conversations_data = []
            for conv in conversations:
                try:
                    if isinstance(conv, dict):
                        # Asegurar que tenga mensajes
                        if 'messages' not in conv or not isinstance(conv['messages'], list):
                            conv['messages'] = []
                        conversations_data.append(conv)
                    else:
                        # Serializar mensajes manualmente si es necesario
                        messages = []
                        if hasattr(conv, 'messages') and conv.messages is not None:
                            for msg in conv.messages:
                                try:
                                    messages.append(msg.to_dict())
                                except Exception as e:
                                    logger.error(f"Error serializando mensaje (ID: {getattr(msg, 'id', None)}): {str(e)}")
                        conversations_data.append({
                            'id': getattr(conv, 'id', None),
                            'user_id': getattr(conv, 'user_id', None),
                            'title': getattr(conv, 'title', None),
                            'created_at': str(getattr(conv, 'created_at', '')),
                            'messages': messages
                        })
                except Exception as e:
                    logger.error(f"Error al convertir conversación a dict (ID: {getattr(conv, 'id', None)}): {str(e)}")
                    conversations_data.append({
                        'id': getattr(conv, 'id', None),
                        'user_id': getattr(conv, 'user_id', None),
                        'title': getattr(conv, 'title', None),
                        'created_at': str(getattr(conv, 'created_at', '')),
                        'messages': []
                    })
            
            logger.info(f"Se encontraron {len(conversations_data)} conversaciones para usuario {user_id}")
            return ResponseDTO.success_response(
                "Conversaciones obtenidas exitosamente",
                data=conversations_data
            )
        except Exception as e:
            logger.error(f"Error al obtener conversaciones: {str(e)}\n{traceback.format_exc()}")
            return ResponseDTO.error_response(
                f"Error interno: {str(e)}",
                error_code="INTERNAL_ERROR"
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
        
        # CORRECCIÓN: Usar query_ai_model() en lugar de generate_response()
        response = self.ai_service.query_ai_model(
            text,
            max_length=getattr(Config, 'AI_MAX_LENGTH', 1000)
        )
        
        if not response:
            return "Lo siento, no pude generar una respuesta en este momento."
        
        return response