from flask import Flask
from flask_cors import CORS
from config import Config
from models import db
from services.ai_service import AIService
from services.agnostic.task.messaging_capability import MessagingCapability
from services.non_agnostic.api_controller import APIController

def create_app(config_class=Config):
    """Factory para crear la aplicación Flask"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Inicializar extensiones
    db.init_app(app)
    CORS(app)
    
    # Crear base de datos
    with app.app_context():
        # Eliminar todas las tablas existentes
        db.drop_all()
        print("Base de datos eliminada")
        
        # Crear todas las tablas nuevamente
        db.create_all()
        print("Base de datos inicializada con nuevo esquema")
    
    # Inicializar servicios
    # Capa Agnóstica
    ai_service = AIService(model_name=Config.AI_MODEL_NAME)
    print("Cargando modelo de IA...")
    ai_service.load_model()
    
    # Task Service (combina servicios de entidad y utilidad)
    messaging_capability = MessagingCapability(ai_service)
    
    # Capa No Agnóstica (Transporte)
    api_controller = APIController(messaging_capability)
    
    # ========================================
    # REGISTRAR RUTAS (Capa No Agnóstica)
    # ========================================
    
    # Rutas de usuarios
    @app.route('/api/users/register', methods=['POST'])
    def register():
        """Registrar nuevo usuario"""
        return api_controller.register_user()
    
    @app.route('/api/users/login', methods=['POST'])
    def login():
        """Autenticar usuario"""
        return api_controller.login_user()
    
    @app.route('/api/users/<int:user_id>/conversations', methods=['GET'])
    def get_user_conversations(user_id):
        """Obtener conversaciones de un usuario"""
        return api_controller.get_user_conversations(user_id)
    
    # Rutas de conversaciones
    @app.route('/api/conversations', methods=['POST'])
    def create_conversation():
        """Crear nueva conversación"""
        return api_controller.create_conversation()
    
    @app.route('/api/conversations/<int:session_id>', methods=['GET'])
    def get_conversation(session_id):
        """Obtener historial de conversación"""
        return api_controller.get_conversation_history(session_id)
    
    # Rutas de mensajes
    @app.route('/api/messages', methods=['POST'])
    def send_message():
        """Enviar mensaje en conversación"""
        return api_controller.send_message()
    
    # Ruta de prueba
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Verificar estado del servicio"""
        return {
            'status': 'ok',
            'ai_service_ready': ai_service.is_ready()
        }
    
    return app

# ========================================
# PUNTO DE ENTRADA
# ========================================
if __name__ == '__main__':
    app = create_app()
    print("\n" + "="*60)
    print("🚀 APLICACIÓN DE CHAT IA INICIADA")
    print("="*60)
    print("\n📋 ARQUITECTURA IMPLEMENTADA:")
    print("   ✓ Functional Decomposition")
    print("   ✓ Service Encapsulation")
    print("   ✓ Agnostic Context")
    print("   ✓ Non-Agnostic Context")
    print("   ✓ Service Layers")
    print("   ✓ Canonical Expression")
    print("\n🏗️  ESTRUCTURA DE CAPAS:")
    print("   Capa 1 (Agnóstica):")
    print("      - Entity Services: UserService, MessageService, ConversationService")
    print("      - Utility Services: TextUtils, TimeUtils")
    print("      - AI Service: AIService")
    print("   Capa 2 (Task Services):")
    print("      - MessagingCapability")
    print("   Capa 3 (No Agnóstica/Transporte):")
    print("      - APIController")
    print("      - ResponseHandler")
    print("\n🔗 ENDPOINTS DISPONIBLES:")
    print("   POST   /api/users/register")
    print("   POST   /api/users/login")
    print("   GET    /api/users/<user_id>/conversations")
    print("   POST   /api/conversations")
    print("   GET    /api/conversations/<session_id>")
    print("   POST   /api/messages")
    print("   GET    /api/health")
    print("\n" + "="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)