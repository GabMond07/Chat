class ResponseDTO:
    STATUS_SUCCESS = "success"
    STATUS_ERROR = "error"
    
    def __init__(self, status, data=None, error=None, message=None):
        self.status = status
        self.data = data
        self.error = error
        self.message = message
        
    def to_dict(self):
        response = {
            "status": self.status
        }
        if self.data is not None:
            response["data"] = self.data
        if self.error is not None:
            response["error"] = self.error
        if self.message is not None:
            if self.data is None:
                response["data"] = {"message": self.message}
            else:
                response["data"]["message"] = self.message
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
        return cls(cls.STATUS_SUCCESS, data=data, message=message)
        return cls(cls.STATUS_SUCCESS, data=data, message=message)
    
    @classmethod
    def error_response(cls, message, error_code=None):
        """
        Crea una respuesta de error
        
        Args:
            message: Mensaje de error
            error_code: Código de error opcional
            
        Returns:
            ResponseDTO: Instancia con estado error
        """
        error = {"message": message}
        if error_code:
            error["code"] = error_code
        return cls(cls.STATUS_ERROR, error=error)