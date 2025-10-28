from flask import jsonify
from dtos import ResponseDTO

class ResponseHandler:
    """
    Servicio No Agnóstico: Manejo de respuestas HTTP
    Dependiente de Flask - Capa de Transporte
    """
    
    @staticmethod
    def send_response(response_dto: ResponseDTO):
        """
        Convierte un ResponseDTO en una respuesta HTTP
        
        Args:
            response_dto: ResponseDTO a convertir
            
        Returns:
            Respuesta JSON de Flask
        """
        if response_dto.success:
            return ResponseHandler.send_success(
                message=response_dto.message,
                data=response_dto.data,
                status_code=200 if response_dto.data else 204
            )
        else:
            return ResponseHandler.send_error(
                message=response_dto.message,
                error_code=response_dto.error_code,
                status_code=response_dto.status_code
            )
    
    # Mapeo de códigos de error a códigos HTTP
    ERROR_CODE_MAP = {
        'USER_NOT_FOUND': 404,
        'CONVERSATION_NOT_FOUND': 404,
        'UNAUTHORIZED': 403,
        'INVALID_INPUT': 400,
        'VALIDATION_ERROR': 400,
        'CREATE_ERROR': 400,
        'SAVE_ERROR': 500,
        'AI_ERROR': 503,
        'INTERNAL_ERROR': 500
    }
    
    @staticmethod
    def send_success(message: str = None, data: dict = None, status_code: int = 200):
        """
        Envía una respuesta de éxito
        
        Args:
            message: Mensaje de éxito opcional
            data: Datos a incluir en la respuesta
            status_code: Código HTTP (default 200)
            
        Returns:
            Respuesta JSON de Flask
        """
        response_dto = ResponseDTO.success_response(message=message, data=data)
        return jsonify(response_dto.to_dict()), status_code

    @staticmethod
    def send_error(message: str, error_code: str = None, status_code: int = None):
        """
        Envía una respuesta de error
        
        Args:
            message: Mensaje de error
            error_code: Código de error para identificación
            status_code: Código HTTP (opcional, se determina por error_code)
            
        Returns:
            Respuesta JSON de Flask
        """
        error = {"message": message}
        if error_code:
            error["code"] = error_code
            # Si no se especifica status_code, usar el mapeo
            if status_code is None:
                status_code = ResponseHandler.ERROR_CODE_MAP.get(error_code, 400)
            
        response_dto = ResponseDTO(
            ResponseDTO.STATUS_ERROR,
            error=error
        )
        return jsonify(response_dto.to_dict()), status_code or 400
    
    @staticmethod
    def format_validation_error(errors: dict):
        """
        Formatea errores de validación
        
        Args:
            errors: Diccionario de errores
        
        Returns:
            Respuesta JSON formateada
        """
        return ResponseHandler.send_error(
            "Error de validación",
            error_code="VALIDATION_ERROR",
            status_code=400
        )