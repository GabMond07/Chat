from datetime import datetime

class TimeUtils:
    """
    Utilidad para manejo de tiempo y fechas
    """
    
    @staticmethod
    def get_current_timestamp():
        """
        Obtiene el timestamp actual en formato ISO
        """
        return datetime.now().isoformat()

    @staticmethod
    def format_timestamp(timestamp):
        """
        Formatea un timestamp para mostrar
        
        Args:
            timestamp: Timestamp en formato ISO
            
        Returns:
            str: Timestamp formateado
        """
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        return timestamp.strftime("%Y-%m-%d %H:%M:%S")
        
    @staticmethod
    def parse_timestamp(timestamp_str):
        """
        Convierte un string de timestamp a objeto datetime
        
        Args:
            timestamp_str: String de timestamp en formato ISO
            
        Returns:
            datetime: Objeto datetime
        """
        return datetime.fromisoformat(timestamp_str)