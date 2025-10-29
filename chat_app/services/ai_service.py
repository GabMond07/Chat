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
            if self._is_loaded and self.model is not None and self.tokenizer is not None:
                print("Modelo ya está cargado")
                return True
                
            print(f"Cargando modelo {self.model_name}...")
            
            # Validar que estamos usando un modelo compatible
            if not (self.model_name.startswith("microsoft/DialoGPT") or 
                   self.model_name.startswith("facebook/blenderbot") or
                   "/" in self.model_name):  # Para modelos locales o personalizados
                raise ValueError(f"Modelo no soportado: {self.model_name}. Use DialoGPT o un modelo compatible con generación de texto.")
            
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
            self._is_loaded = True
            print(f"Modelo {self.model_name} cargado exitosamente")
            return True
        except Exception as e:
            print(f"Error al cargar modelo {self.model_name}: {str(e)}")
            self._is_loaded = False
            self.model = None
            self.tokenizer = None
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
            print("Modelo no está listo (not is_ready())")
            return None
            
        if not self.tokenizer or not self.model:
            print("Tokenizer o modelo no inicializados")
            return None
        
        try:
            print(f"Procesando entrada: '{input_text}'")
            # Tokenizar entrada
            inputs = self.tokenizer.encode(input_text + self.tokenizer.eos_token, 
                                          return_tensors='pt')
            
            print("Input tokenizado, generando respuesta...")
            # Generar respuesta con parámetros ajustados
            outputs = self.model.generate(
                inputs,
                max_length=max_length,
                min_length=20,  # Asegurar respuestas no muy cortas
                pad_token_id=self.tokenizer.eos_token_id,
                do_sample=True,
                temperature=0.7,  # Controlar creatividad
                top_p=0.9,
                top_k=50,
                num_return_sequences=1,
                no_repeat_ngram_size=2  # Evitar repeticiones
            )
            
            print("Respuesta generada, decodificando...")
            # Decodificar respuesta
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Remover el input del output y limpiar
            if response.startswith(input_text):
                response = response[len(input_text):].strip()
            
            print(f"Respuesta final: '{response[:100]}...'")
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