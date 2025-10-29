import re
import html
from typing import Tuple, Dict, Any

# Constantes de validación
EMAIL_MAX_LENGTH = 254  # RFC 5321
USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 30
MESSAGE_MIN_LENGTH = 1
MESSAGE_MAX_LENGTH = 2000

# Patrones de validación
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')
# Lista de palabras prohibidas o spam (expandir según necesidades)
BLOCKED_WORDS = {'spam', 'hack', 'virus', 'malware'}
# Caracteres especiales permitidos en mensajes
ALLOWED_SPECIAL_CHARS = set('.,!?¡¿@#$%()*+-/\\:; ')

def validate_email(email: str) -> Tuple[bool, str]:
    """
    Valida el formato y seguridad del email.
    
    Args:
        email: dirección de correo a validar
        
    Returns:
        Tupla (es_válido, mensaje_error)
    """
    if not email:
        return False, "El email es requerido"
        
    email = email.strip().lower()
    
    if len(email) > EMAIL_MAX_LENGTH:
        return False, f"El email no puede exceder {EMAIL_MAX_LENGTH} caracteres"
        
    if not EMAIL_PATTERN.match(email):
        return False, "Formato de email inválido"
        
    # Validar contra inyección de headers
    if '\\n' in email or '\\r' in email:
        return False, "Email contiene caracteres inválidos"
        
    return True, ""

def validate_username(username: str) -> Tuple[bool, str]:
    """
    Valida el formato y seguridad del nombre de usuario.
    
    Args:
        username: nombre de usuario a validar
        
    Returns:
        Tupla (es_válido, mensaje_error)
    """
    if not username:
        return False, "El nombre de usuario es requerido"
        
    username = username.strip()
    
    if len(username) < USERNAME_MIN_LENGTH:
        return False, f"El nombre de usuario debe tener al menos {USERNAME_MIN_LENGTH} caracteres"
        
    if len(username) > USERNAME_MAX_LENGTH:
        return False, f"El nombre de usuario no puede exceder {USERNAME_MAX_LENGTH} caracteres"
        
    if not USERNAME_PATTERN.match(username):
        return False, "El nombre de usuario solo puede contener letras, números, guiones y guiones bajos"
        
    # Validar contra XSS
    if '<' in username or '>' in username:
        return False, "El nombre de usuario contiene caracteres no permitidos"
        
    return True, ""

def validate_message_content(content: str) -> Tuple[bool, Dict[str, Any]]:
    """
    Valida y limpia el contenido del mensaje.
    
    Args:
        content: contenido del mensaje a validar
        
    Returns:
        Tupla (es_válido, resultado)
        resultado contiene:
            - cleaned_content: contenido limpio si es válido
            - error: mensaje de error si no es válido
            - warnings: lista de advertencias si hay contenido sospechoso
    """
    result = {
        'cleaned_content': None,
        'error': None,
        'warnings': []
    }
    
    if not content:
        result['error'] = "El mensaje está vacío"
        return False, result
        
    # Limpiar espacios innecesarios
    cleaned = ' '.join(content.split())
    
    # Validar longitud
    if len(cleaned) < MESSAGE_MIN_LENGTH:
        result['error'] = f"El mensaje debe tener al menos {MESSAGE_MIN_LENGTH} caracteres"
        return False, result
        
    if len(cleaned) > MESSAGE_MAX_LENGTH:
        result['error'] = f"El mensaje no puede exceder {MESSAGE_MAX_LENGTH} caracteres"
        return False, result
    
    # Detectar contenido sospechoso
    words = cleaned.lower().split()
    blocked = [word for word in words if word in BLOCKED_WORDS]
    if blocked:
        result['warnings'].append(f"Mensaje contiene palabras potencialmente inapropiadas: {', '.join(blocked)}")
    
    # Validar caracteres especiales
    special_chars = set(c for c in cleaned if not c.isalnum() and c not in ALLOWED_SPECIAL_CHARS)
    if special_chars:
        result['warnings'].append(f"Mensaje contiene caracteres especiales: {', '.join(special_chars)}")
    
    # Detectar URLs sospechosas
    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', cleaned)
    if urls:
        result['warnings'].append(f"Mensaje contiene URLs que requieren revisión: {len(urls)} encontradas")
    
    # Limpiar contra XSS
    cleaned = html.escape(cleaned)
    
    # Validar repeticiones excesivas
    if any(c * 5 in cleaned for c in set(cleaned)):
        result['warnings'].append("Mensaje contiene caracteres repetidos excesivamente")
    
    result['cleaned_content'] = cleaned
    return True, result

def sanitize_input(text: str) -> str:
    """
    Sanitiza una entrada de texto para prevenir inyecciones.
    
    Args:
        text: texto a sanitizar
        
    Returns:
        Texto sanitizado
    """
    if not text:
        return ""
        
    # Remover caracteres de control
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
    
    # Escapar HTML
    text = html.escape(text)
    
    # Normalizar espacios
    text = ' '.join(text.split())
    
    return text