from flask import request
from dtos import UserDTO, CredentialsDTO, MessageDTO, ConversationDTO
from services.non_agnostic.response_handler import ResponseHandler
from services.agnostic.entity.user_service import UserService
from services.agnostic.task.messaging_capability import MessagingCapability

class APIController:
    """
    Servicio No Agnóstico: Controlador de API
    Dependiente de Flask - Capa de Transporte
    Solo traduce protocolos (HTTP/JSON) a DTOs canónicos
    """
    
    def __init__(self, messaging_capability: MessagingCapability):
        """
        Inicializa el controlador
        
        Args:
            messaging_capability: Servicio de capacidad de mensajería
        """
        self.messaging_capability = messaging_capability
    
    def register_user(self):
        """
        Endpoint: Registrar nuevo usuario
        POST /api/users/register
        """
        try:
            data = request.get_json()
            
            # Validar datos requeridos
            if not data or 'username' not in data or 'password' not in data or 'email' not in data:
                return ResponseHandler.send_error(
                    "Datos incompletos",
                    error_code="INVALID_INPUT"
                )
            
            # Convertir JSON a DTO
            user_dto = UserDTO(
                username=data['username'],
                email=data['email'],
                is_active=data.get('is_active', True)
            )
            
            # Llamar servicio agnóstico
            created_user = UserService.create_user(user_dto, data['password'])
            
            if not created_user:
                return ResponseHandler.send_error(
                    "Error al crear usuario. El usuario o email ya existe.",
                    error_code="CREATE_ERROR"
                )
            
            return ResponseHandler.send_success(
                "Usuario creado exitosamente",
                data=created_user.to_dict(),
                status_code=201
            )
            
        except Exception as e:
            return ResponseHandler.send_error(
                f"Error interno: {str(e)}",
                error_code="INTERNAL_ERROR",
                status_code=500
            )
    
    def login_user(self):
        """
        Endpoint: Autenticar usuario
        POST /api/users/login
        """
        try:
            data = request.get_json()
            
            # Validar datos
            if not data or 'username' not in data or 'password' not in data:
                return ResponseHandler.send_error(
                    "Credenciales incompletas",
                    error_code="INVALID_INPUT"
                )
            
            # Convertir a DTO
            credentials = CredentialsDTO(
                username=data['username'],
                password=data['password']
            )
            
            # Autenticar
            user = UserService.authenticate(credentials)
            
            if not user:
                return ResponseHandler.send_error(
                    "Credenciales inválidas",
                    error_code="UNAUTHORIZED",
                    status_code=401
                )
            
            return ResponseHandler.send_success(
                "Login exitoso",
                data=user.to_dict()
            )
            
        except Exception as e:
            return ResponseHandler.send_error(
                f"Error interno: {str(e)}",
                error_code="INTERNAL_ERROR",
                status_code=500
            )
    
    def create_conversation(self):
        """
        Endpoint: Crear nueva conversación
        POST /api/conversations
        """
        try:
            data = request.get_json()
            
            # Validar datos
            if not data or 'user_id' not in data:
                return ResponseHandler.send_error(
                    "user_id es requerido",
                    error_code="INVALID_INPUT"
                )
            
            user_id = data['user_id']
            title = data.get('title', 'Nueva Conversación')
            
            # Llamar task service
            result = self.messaging_capability.create_new_conversation(user_id, title)
            
            # Convertir ResponseDTO a respuesta HTTP
            return ResponseHandler.send_response(result)
            
        except Exception as e:
            return ResponseHandler.send_error(
                f"Error interno: {str(e)}",
                error_code="INTERNAL_ERROR",
                status_code=500
            )
    
    def send_message(self):
        """
        Endpoint: Enviar mensaje en conversación
        POST /api/messages
        """
        try:
            data = request.get_json()
            
            # Validar datos requeridos
            required_fields = ['user_id', 'session_id', 'content']
            for field in required_fields:
                if field not in data:
                    return ResponseHandler.send_error(
                        f"Campo requerido: {field}",
                        error_code="INVALID_INPUT"
                    )
            
            user_id = data['user_id']
            session_id = data['session_id']
            content = data['content']
            
            # Llamar task service (orquesta todo el flujo)
            result = self.messaging_capability.process_user_message(
                user_id, session_id, content
            )
            
            # Convertir ResponseDTO a respuesta HTTP
            return ResponseHandler.send_response(result)
            
        except Exception as e:
            return ResponseHandler.send_error(
                f"Error interno: {str(e)}",
                error_code="INTERNAL_ERROR",
                status_code=500
            )
    
    def get_conversation_history(self, session_id: int):
        """
        Endpoint: Obtener historial de conversación
        GET /api/conversations/<session_id>
        """
        try:
            # Obtener user_id de query params o headers
            user_id = request.args.get('user_id', type=int)
            
            if not user_id:
                return ResponseHandler.send_error(
                    "user_id es requerido",
                    error_code="INVALID_INPUT"
                )
            
            # Llamar task service
            result = self.messaging_capability.get_conversation_history(
                user_id, session_id
            )
            
            return ResponseHandler.send_response(result)
            
        except Exception as e:
            return ResponseHandler.send_error(
                f"Error interno: {str(e)}",
                error_code="INTERNAL_ERROR",
                status_code=500
            )
    
    def get_user_conversations(self, user_id: int):
        """
        Endpoint: Obtener todas las conversaciones de un usuario
        GET /api/users/<user_id>/conversations
        """
        try:
            # Llamar task service
            result = self.messaging_capability.get_user_conversations(user_id)
            
            return ResponseHandler.send_json_response(result)
            
        except Exception as e:
            return ResponseHandler.send_error(
                f"Error interno: {str(e)}",
                error_code="INTERNAL_ERROR",
                status_code=500
            )