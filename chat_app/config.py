class Config:
    # Configuración básica de la aplicación
    SECRET_KEY = "your-secret-key"
    DEBUG = True
    
    # Configuración de la base de datos
    SQLALCHEMY_DATABASE_URI = 'sqlite:///chat_app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración del modelo de IA
    AI_MODEL_NAME = "microsoft/DialoGPT-small"  # Modelo más ligero para desarrollo
    AI_MAX_LENGTH = 1000  # Longitud máxima de la respuesta
    AI_TEMPERATURE = 0.7  # Temperatura para la generación de texto (0-1)
    
    # Configuración de la API
    API_VERSION = "v1"
    API_PREFIX = f"/api/{API_VERSION}"
    
    # Configuración de seguridad
    JWT_SECRET_KEY = "your-jwt-secret-key"
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hora
    
    # Configuración de logs
    LOG_LEVEL = "INFO"