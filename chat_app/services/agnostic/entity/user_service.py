from typing import Optional
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from dtos import UserDTO, CredentialsDTO

class UserService:
    """
    Servicio de Entidad para Usuario (Agnóstico)
    Sigue convenciones CRUD canónicas
    """
    
    @staticmethod
    def create_user(user_data: UserDTO, password: str) -> Optional[UserDTO]:
        """
        Registra un nuevo usuario
        
        Args:
            user_data: DTO con datos del usuario
            password: Contraseña sin hashear
        
        Returns:
            UserDTO del usuario creado o None si hay error
        """
        try:
            # Verificar si el usuario ya existe
            existing_user = User.query.filter(
                (User.username == user_data.username) | 
                (User.email == user_data.email)
            ).first()
            
            if existing_user:
                return None
            
            # Crear nuevo usuario
            new_user = User(
                username=user_data.username,
                email=user_data.email,
                password=password,  # El modelo User se encarga del hash
                is_active=user_data.is_active
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            # Convertir a DTO
            return UserService._user_to_dto(new_user)
            
        except Exception as e:
            db.session.rollback()
            print(f"Error al crear usuario: {str(e)}")
            return None
    
    @staticmethod
    def get_user(user_id: int) -> Optional[UserDTO]:
        """
        Obtiene información del usuario por ID
        
        Args:
            user_id: ID del usuario
        
        Returns:
            UserDTO o None si no existe
        """
        user = User.query.get(user_id)
        if not user:
            return None
        
        return UserService._user_to_dto(user)
    
    @staticmethod
    def get_user_by_username(username: str) -> Optional[UserDTO]:
        """
        Obtiene usuario por nombre de usuario
        
        Args:
            username: Nombre de usuario
        
        Returns:
            UserDTO o None si no existe
        """
        user = User.query.filter_by(username=username).first()
        if not user:
            return None
        
        return UserService._user_to_dto(user)
    
    @staticmethod
    def update_user(user_id: int, update_data: UserDTO) -> Optional[UserDTO]:
        """
        Actualiza datos del usuario
        
        Args:
            user_id: ID del usuario
            update_data: DTO con datos a actualizar
        
        Returns:
            UserDTO actualizado o None si hay error
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return None
            
            # Actualizar campos
            if update_data.username:
                user.username = update_data.username
            if update_data.email:
                user.email = update_data.email
            user.is_active = update_data.is_active
            
            db.session.commit()
            
            return UserService._user_to_dto(user)
            
        except Exception as e:
            db.session.rollback()
            print(f"Error al actualizar usuario: {str(e)}")
            return None
    
    @staticmethod
    def delete_user(user_id: int) -> bool:
        """
        Elimina usuario
        
        Args:
            user_id: ID del usuario
        
        Returns:
            True si se eliminó exitosamente
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return False
            
            db.session.delete(user)
            db.session.commit()
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"Error al eliminar usuario: {str(e)}")
            return False
    
    @staticmethod
    def authenticate(credentials: CredentialsDTO) -> Optional[UserDTO]:
        """
        Autentica usuario con credenciales
        
        Args:
            credentials: DTO con username y password
        
        Returns:
            UserDTO si la autenticación es exitosa, None si falla
        """
        user = User.query.filter_by(username=credentials.username).first()
        
        if not user or not user.is_active:
            return None
        
        if not check_password_hash(user.password_hash, credentials.password):
            return None
        
        return UserService._user_to_dto(user)
    
    @staticmethod
    def _user_to_dto(user: User) -> UserDTO:
        """Convierte modelo User a UserDTO"""
        return UserDTO(
            id=user.id,
            username=user.username,
            email=user.email,
            created_at=user.created_at,
            is_active=user.is_active
        )