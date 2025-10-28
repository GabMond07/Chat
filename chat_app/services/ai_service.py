from typing import Optional, Dict, Any
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

class AIService:
    """
    Servicio Agnóstico para consultar IA
    Encapsula la lógica de comunicación con modelos de lenguaje
    """
    
    def __init__(self, model_name: str = "microsoft/DialoGPT-medium"):
        """
        Inicializa el servicio de IA
        
        Args:
            model_name: Nombre del modelo en HuggingFace
        """
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self._is_loaded = False
    
    def load_model(self) -> bool:
        """
        Carga el modelo de IA
        
        Returns:
            True si el modelo se cargó exitosamente
        """
        try:
            print(f"Cargando modelo {self.model_name}...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
            self._is_loaded = True
            print("Modelo cargado exitosamente")
            return True
        except Exception as e:
            print(f"Error al cargar modelo: {str(e)}")
            self._is_loaded = False
            return False
    
    def is_ready(self) -> bool:
        """Verifica si el servicio está listo para generar respuestas"""
        return self._is_loaded
    
    def query_ai_model(self, input_text: str, max_length: int = 1000) -> Optional[str]:
        """
        Consulta genérica al modelo de IA
        
        Args:
            input_text: Texto de entrada para el modelo
            max_length: Longitud máxima de la respuesta
        
        Returns:
            Texto generado por el modelo o None si hay error
        """
        if not self.is_ready():
            return None
        
        try:
            # Tokenizar entrada
            inputs = self.tokenizer.encode(input_text + self.tokenizer.eos_token, 
                                          return_tensors='pt')
            
            # Generar respuesta
            outputs = self.model.generate(
                inputs,
                max_length=max_length,
                pad_token_id=self.tokenizer.eos_token_id,
                do_sample=True,
                top_p=0.92,
                top_k=50
            )
            
            # Decodificar respuesta
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Remover el input del output
            if response.startswith(input_text):
                response = response[len(input_text):].strip()
            
            return response
            
        except Exception as e:
            print(f"Error al generar respuesta: {str(e)}")
            return None
    
    def analyze_with_ai(self, input_text: str) -> Dict[str, Any]:
        """
        Analiza texto con IA (para análisis de sentimiento, clasificación, etc.)
        
        Args:
            input_text: Texto a analizar
        
        Returns:
            Diccionario con resultados del análisis
        """
        # Implementación básica - puede expandirse según necesidades
        response = self.query_ai_model(input_text, max_length=50)
        
        return {
            'input': input_text,
            'response': response,
            'model': self.model_name,
            'success': response is not None
        }
    
    def predict_intent(self, input_text: str) -> str:
        """
        Predice la intención del usuario (clasificación básica)
        
        Args:
            input_text: Texto del usuario
        
        Returns:
            Intención detectada
        """
        # Implementación simplificada
        text_lower = input_text.lower()
        
        if any(word in text_lower for word in ['hola', 'buenos días', 'buenas tardes']):
            return 'greeting'
        elif any(word in text_lower for word in ['adiós', 'hasta luego', 'chao']):
            return 'farewell'
        elif '?' in text_lower:
            return 'question'
        else:
            return 'statement'