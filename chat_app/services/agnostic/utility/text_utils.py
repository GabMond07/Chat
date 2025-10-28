import re
from typing import Optional

class TextUtils:
    """Servicio de Utilidad para procesamiento de texto (Agnóstico)"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Limpia y normaliza texto"""
        if not text:
            return ""
        
        # Eliminar espacios múltiples
        text = re.sub(r'\s+', ' ', text)
        
        # Eliminar espacios al inicio y final
        text = text.strip()
        
        return text
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitiza entrada del usuario para evitar inyecciones"""
        if not text:
            return ""
        
        # Eliminar caracteres potencialmente peligrosos
        text = re.sub(r'[<>{}]', '', text)
        
        # Limpiar texto
        text = TextUtils.clean_text(text)
        
        return text
    
    @staticmethod
    def truncate_text(text: str, max_length: int) -> str:
        """Trunca texto a una longitud máxima"""
        if not text or len(text) <= max_length:
            return text
        
        return text[:max_length] + "..."
    
    @staticmethod
    def validate_length(text: str, min_length: int, max_length: int) -> tuple[bool, Optional[str]]:
        """Valida la longitud del texto"""
        if not text:
            return False, "El texto no puede estar vacío"
        
        text_length = len(text)
        
        if text_length < min_length:
            return False, f"El texto debe tener al menos {min_length} caracteres"
        
        if text_length > max_length:
            return False, f"El texto no puede exceder {max_length} caracteres"
        
        return True, None
    
    @staticmethod
    def contains_offensive_content(text: str) -> bool:
        """Verifica si el texto contiene contenido ofensivo básico"""
        # Lista básica de palabras prohibidas (expandir según necesidades)
        offensive_words = ['spam', 'scam']  # Agregar más según contexto
        
        text_lower = text.lower()
        return any(word in text_lower for word in offensive_words)