class ResponseDTO:
    STATUS_SUCCESS = "success"
    STATUS_ERROR = "error"
    
    def __init__(self, status, data=None, error=None, message=None, error_code=None, status_code=None):
        self.status = status
        self.success = status == self.STATUS_SUCCESS
        self.data = data
        self.error = error
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        
    def to_dict(self):
        response = {
            "status": self.status,
            "success": self.success
        }
        
        if self.success:
            if self.data is not None:
                if isinstance(self.data, dict):
                    response["data"] = self.data
                else:
                    response["data"] = self.data.to_dict() if hasattr(self.data, 'to_dict') else self.data
            if self.message is not None:
                if "data" not in response:
                    response["data"] = {}
                response["data"]["message"] = self.message
        else:
            if self.error_code or self.message:
                response["error"] = {
                    "code": self.error_code or "INTERNAL_ERROR",
                    "message": self.message or "Error desconocido"
                }
            
        return response
    
    @classmethod
    def success_response(cls, message=None, data=None):
        """
        Crea una respuesta de éxito
        
        Args:
            message: Mensaje de éxito opcional
            data: Datos a incluir en la respuesta
            
        Returns:
            ResponseDTO: Instancia con estado success
        """
        return cls(
            status=cls.STATUS_SUCCESS,
            data=data,
            message=message,
            status_code=200 if data is not None else 204
        )
    
    @classmethod
    def error_response(cls, message, error_code=None, status_code=None):
        """
        Crea una respuesta de error
        
        Args:
            message: Mensaje de error
            error_code: Código de error opcional
            status_code: Código HTTP opcional
            
        Returns:
            ResponseDTO: Instancia con estado error
        """
        return cls(
            status=cls.STATUS_ERROR,
            message=message,
            error_code=error_code,
            status_code=status_code or 400
        )