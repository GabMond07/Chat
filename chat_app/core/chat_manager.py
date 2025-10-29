from services.ai_service import AIService
from services.agnostic.task.messaging_capability import MessagingCapability
from utils.logger import logger
from dtos import ResponseDTO

class ChatManager:
    def __init__(self):
        """
        Inicializa el gestor de chat
        """
        self.ai_service = AIService(model_name="microsoft/DialoGPT-medium")  # Usar el modelo de DialoGPT
        self.messaging_capability = MessagingCapability(self.ai_service)
        logger.info("ChatManager inicializado con servicios")

    def process_message(self, data: dict) -> dict:
        """
        Procesa mensajes entrantes del chat
        
        Args:
            data: Diccionario con datos del mensaje
                {
                    "user_id": int,
                    "session_id": int,
                    "content": str
                }
        
        Returns:
            dict: Respuesta procesada
        """
        try:
            logger.debug(f"Procesando mensaje: {data}")
            
            # Validar datos requeridos
            required_fields = ['user_id', 'session_id', 'content']
            for field in required_fields:
                if field not in data:
                    logger.warning(f"Campo requerido faltante: {field}")
                    return ResponseDTO.error_response(
                        f"Campo requerido: {field}",
                        error_code="INVALID_INPUT"
                    ).to_dict()

            # Procesar mensaje usando el servicio de mensajería
            result = self.messaging_capability.process_user_message(
                user_id=data['user_id'],
                session_id=data['session_id'],
                message_content=data['content']
            )
            
            return result.to_dict()
            
        except Exception as e:
            logger.error(f"Error procesando mensaje: {str(e)}", exc_info=True)
            return ResponseDTO.error_response(
                "Error interno del servidor",
                error_code="INTERNAL_ERROR"
            ).to_dict()