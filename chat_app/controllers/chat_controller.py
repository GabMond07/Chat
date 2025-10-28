from flask import Blueprint, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from core.chat_manager import ChatManager
from core.chat_room_manager import ChatRoomManager
from services.non_agnostic.response_handler import ResponseHandler
from utils.logger import logger

chat_bp = Blueprint('chat', __name__)
socketio = SocketIO(cors_allowed_origins="*")
chat_manager = ChatManager()
room_manager = ChatRoomManager()

# ===================================
# WebSocket Events
# ===================================

@socketio.on('connect')
def handle_connect():
    """
    Maneja la conexión de un cliente WebSocket
    """
    logger.info(f"Nuevo cliente conectado: {request.sid}")

@socketio.on('join')
def handle_join(data):
    """
    Usuario se une a una sala de chat
    
    Datos esperados:
    {
        "user_id": int,
        "session_id": int
    }
    """
    try:
        user_id = data.get('user_id')
        session_id = data.get('session_id')
        
        if not user_id or not session_id:
            emit('error', {
                'message': 'user_id y session_id son requeridos'
            })
            return
            
        # Unirse a la sala
        join_room(f"chat_{session_id}")
        room_manager.join_room(session_id, user_id, request.sid)
        
        # Notificar a otros usuarios
        participants = room_manager.get_room_participants(session_id)
        emit('user_joined', {
            'user_id': user_id,
            'active_users': list(participants.keys())
        }, room=f"chat_{session_id}")
        
        logger.info(f"Usuario {user_id} se unió a la sala {session_id}")
        
    except Exception as e:
        logger.error(f"Error en join: {str(e)}", exc_info=True)
        emit('error', {'message': 'Error interno del servidor'})

@socketio.on('leave')
def handle_leave(data):
    """
    Usuario sale de una sala de chat
    """
    try:
        user_id = data.get('user_id')
        session_id = data.get('session_id')
        
        if not user_id or not session_id:
            return
            
        leave_room(f"chat_{session_id}")
        room_manager.leave_room(session_id, user_id, request.sid)
        
        # Notificar a otros usuarios
        emit('user_left', {
            'user_id': user_id
        }, room=f"chat_{session_id}")
        
        logger.info(f"Usuario {user_id} salió de la sala {session_id}")
        
    except Exception as e:
        logger.error(f"Error en leave: {str(e)}", exc_info=True)

@socketio.on('typing')
def handle_typing(data):
    """
    Usuario está escribiendo
    """
    try:
        user_id = data.get('user_id')
        session_id = data.get('session_id')
        is_typing = data.get('typing', False)
        
        if not user_id or not session_id:
            return
            
        room_manager.set_typing(session_id, user_id, is_typing)
        
        # Notificar a otros usuarios
        emit('user_typing', {
            'user_id': user_id,
            'typing': is_typing
        }, room=f"chat_{session_id}")
        
    except Exception as e:
        logger.error(f"Error en typing: {str(e)}", exc_info=True)

@socketio.on('message')
def handle_message(data):
    """
    Nuevo mensaje de chat
    """
    try:
        # Validar datos
        required_fields = ['user_id', 'session_id', 'content']
        if not all(field in data for field in required_fields):
            emit('error', {
                'message': 'Datos incompletos'
            })
            return
        
        # Procesar mensaje usando el API existente
        result = chat_manager.messaging_capability.process_user_message(
            user_id=data['user_id'],
            session_id=data['session_id'],
            message_content=data['content']
        )
        
        if result.success:
            # Emitir mensaje a todos en la sala
            emit('new_message', result.data, room=f"chat_{data['session_id']}")
        else:
            # Emitir error solo al emisor
            emit('error', {
                'message': result.message,
                'code': result.error_code
            })
            
    except Exception as e:
        logger.error(f"Error procesando mensaje: {str(e)}", exc_info=True)
        emit('error', {'message': 'Error interno del servidor'})

@socketio.on('disconnect')
def handle_disconnect():
    """
    Cliente WebSocket desconectado
    """
    logger.info(f"Cliente desconectado: {request.sid}")

# ===================================
# API REST Endpoints
# ===================================

@chat_bp.route('/status', methods=['GET'])
def get_chat_status():
    """
    Obtiene el estado actual del chat
    - Usuarios activos
    - Usuarios escribiendo
    """
    try:
        active_users = room_manager.get_active_users()
        return jsonify({
            'status': 'success',
            'data': {
                'active_users': len(active_users),
                'active_rooms': len(room_manager.rooms)
            }
        })
    except Exception as e:
        logger.error(f"Error obteniendo estado: {str(e)}", exc_info=True)
        return ResponseHandler.send_error(
            "Error interno del servidor",
            error_code="INTERNAL_ERROR",
            status_code=500
        )