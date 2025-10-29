from flask import Blueprint, request, jsonify, current_app
from flask_socketio import SocketIO, emit, join_room, leave_room
from core.chat_manager import ChatManager
from core.chat_room_manager import ChatRoomManager
from services.non_agnostic.response_handler import ResponseHandler
from utils.logger import logger
import time

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

        user_id = data['user_id']
        session_id = data['session_id']
        content = data['content']
        display_name = data.get('display_name') or f'user_{user_id}'
        room = f"chat_{session_id}"

        # Emitir inmediatamente el mensaje del usuario a la sala
        user_msg = {
            'author': 'user',
            'user_id': user_id,
            'session_id': session_id,
            'content': content,
            'display_name': display_name,
            'timestamp': int(time.time())  # Añadir timestamp
        }
        emit('new_message', user_msg, room=room)
        
        # Indicar que el bot está escribiendo
        socketio.emit('bot_typing', {'status': True}, room=room)

        # Obtener la app fuera de la función background
        app = current_app._get_current_object()

        # Procesar la respuesta del bot en background para no bloquear el socket
        def process_and_emit(app, u_id, s_id, msg_content, disp_name):
            try:
                logger.info(f"Background: procesando mensaje para Session ID: {s_id}")
                room_local = f"chat_{s_id}"
                
                try:
                    with app.app_context():
                        # Intento de procesamiento con timeout implícito
                        result = chat_manager.messaging_capability.process_user_message(
                            user_id=u_id,
                            session_id=s_id,
                            message_content=msg_content
                        )
                        
                        if result and hasattr(result, 'data'):
                            # Procesar la respuesta del bot
                            bot_text = None
                            data_obj = result.data
                            
                            if isinstance(data_obj, dict):
                                # Buscar el texto de la respuesta en las claves comunes
                                for key in ['bot_message', 'bot_response', 'response', 'message', 'content']:
                                    if key in data_obj:
                                        value = data_obj[key]
                                        if isinstance(value, str):
                                            bot_text = value
                                            break
                                        elif isinstance(value, dict) and 'content' in value:
                                            bot_text = value['content']
                                            break
                            elif isinstance(data_obj, str):
                                bot_text = data_obj
                            
                            if not bot_text:
                                bot_text = "Lo siento, no pude generar una respuesta coherente."
                                
                            # Emitir la respuesta del bot
                            bot_msg = {
                                'author': 'bot',
                                'content': bot_text,
                                'timestamp': int(time.time()),
                                'session_id': s_id
                            }

                            socketio.emit('new_message', bot_msg, room=room_local)
                            logger.info(f"Background: respuesta del bot emitida para Session ID: {s_id}")
                        else:
                            socketio.emit('new_message', {
                                'author': 'bot',
                                'content': "Lo siento, estoy teniendo problemas para procesar tu mensaje. ¿Podrías intentarlo de nuevo?",
                                'timestamp': int(time.time()),
                                'session_id': s_id
                            }, room=room_local)
                            logger.warning(f"Background: no se pudo generar respuesta para Session ID: {s_id}")
                            
                except Exception as exc:
                    logger.error(f"Error en process_user_message: {str(exc)}", exc_info=True)
                    socketio.emit('error', {
                        'message': 'Error interno procesando el mensaje'
                    }, room=room_local)
                    
            except Exception as e:
                logger.error(f"Error en background processing: {str(e)}", exc_info=True)
                socketio.emit('error', {
                    'message': 'Error interno procesando la respuesta'
                }, room=room_local)
            finally:
                # Siempre indicar que el bot terminó de escribir
                socketio.emit('bot_typing', {'status': False}, room=room_local)

        socketio.start_background_task(process_and_emit, app, user_id, session_id, content, display_name)

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