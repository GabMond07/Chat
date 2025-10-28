from typing import Dict, Set
from datetime import datetime

class ChatRoomManager:
    """
    Gestor de salas de chat y estado de usuarios
    """
    def __init__(self):
        # {session_id: {user_id: socket_id}}
        self.rooms: Dict[int, Dict[int, str]] = {}
        # {user_id: {socket_id: last_activity}}
        self.active_users: Dict[int, Dict[str, datetime]] = {}
        # {user_id: Set[session_id]}
        self.user_typing: Dict[int, Set[int]] = {}
    
    def join_room(self, session_id: int, user_id: int, socket_id: str):
        """
        Usuario se une a una sala de chat
        """
        if session_id not in self.rooms:
            self.rooms[session_id] = {}
        self.rooms[session_id][user_id] = socket_id
        
        if user_id not in self.active_users:
            self.active_users[user_id] = {}
        self.active_users[user_id][socket_id] = datetime.utcnow()
    
    def leave_room(self, session_id: int, user_id: int, socket_id: str):
        """
        Usuario sale de una sala de chat
        """
        if session_id in self.rooms and user_id in self.rooms[session_id]:
            if self.rooms[session_id][user_id] == socket_id:
                del self.rooms[session_id][user_id]
                if not self.rooms[session_id]:
                    del self.rooms[session_id]
        
        if user_id in self.active_users and socket_id in self.active_users[user_id]:
            del self.active_users[user_id][socket_id]
            if not self.active_users[user_id]:
                del self.active_users[user_id]
    
    def set_typing(self, session_id: int, user_id: int, is_typing: bool):
        """
        Actualiza el estado de typing de un usuario
        """
        if is_typing:
            if user_id not in self.user_typing:
                self.user_typing[user_id] = set()
            self.user_typing[user_id].add(session_id)
        else:
            if user_id in self.user_typing:
                self.user_typing[user_id].discard(session_id)
                if not self.user_typing[user_id]:
                    del self.user_typing[user_id]
    
    def get_room_participants(self, session_id: int) -> Dict[int, str]:
        """
        Obtiene los participantes de una sala
        """
        return self.rooms.get(session_id, {})
    
    def is_user_typing(self, user_id: int, session_id: int) -> bool:
        """
        Verifica si un usuario está escribiendo en una sala
        """
        return user_id in self.user_typing and session_id in self.user_typing[user_id]
    
    def get_active_users(self) -> Dict[int, datetime]:
        """
        Obtiene usuarios activos y su última actividad
        """
        active = {}
        for user_id, sockets in self.active_users.items():
            if sockets:
                active[user_id] = max(sockets.values())
        return active
    
    def update_user_activity(self, user_id: int, socket_id: str):
        """
        Actualiza la última actividad de un usuario
        """
        if user_id in self.active_users and socket_id in self.active_users[user_id]:
            self.active_users[user_id][socket_id] = datetime.utcnow()