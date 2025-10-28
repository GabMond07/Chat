import pytest
from app import create_app
from models import db
import json

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

def test_health_check(client):
    """Prueba el endpoint de health check"""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'ok'
    assert 'ai_service_ready' in data

def test_user_registration(client):
    """Prueba el registro de usuarios"""
    # Caso exitoso
    response = client.post('/api/users/register', json={
        'username': 'testuser',
        'password': 'testpass123',
        'email': 'test@example.com'
    })
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['success'] == True
    assert 'username' in data['data']
    assert data['data']['username'] == 'testuser'

    # Caso de error - datos incompletos
    response = client.post('/api/users/register', json={
        'username': 'testuser2'
    })
    assert response.status_code == 400

def test_user_login(client):
    """Prueba el login de usuarios"""
    # Primero registramos un usuario
    client.post('/api/users/register', json={
        'username': 'logintest',
        'password': 'testpass123',
        'email': 'login@example.com'
    })

    # Caso exitoso
    response = client.post('/api/users/login', json={
        'username': 'logintest',
        'password': 'testpass123'
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert 'username' in data['data']

    # Caso de error - credenciales incorrectas
    response = client.post('/api/users/login', json={
        'username': 'logintest',
        'password': 'wrongpass'
    })
    assert response.status_code == 401

def test_create_conversation(client):
    """Prueba la creación de conversaciones"""
    # Primero registramos y logueamos un usuario
    client.post('/api/users/register', json={
        'username': 'convuser',
        'password': 'testpass123',
        'email': 'conv@example.com'
    })
    login_response = client.post('/api/users/login', json={
        'username': 'convuser',
        'password': 'testpass123'
    })
    user_data = json.loads(login_response.data)['data']

    # Crear conversación
    response = client.post('/api/conversations', json={
        'user_id': user_data['id'],
        'title': 'Test Conversation'
    })
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['success'] == True
    assert 'id' in data['data']

def test_send_message(client):
    """Prueba el envío de mensajes"""
    # Primero creamos un usuario y una conversación
    client.post('/api/users/register', json={
        'username': 'msguser',
        'password': 'testpass123',
        'email': 'msg@example.com'
    })
    login_response = client.post('/api/users/login', json={
        'username': 'msguser',
        'password': 'testpass123'
    })
    user_data = json.loads(login_response.data)['data']
    
    conv_response = client.post('/api/conversations', json={
        'user_id': user_data['id'],
        'title': 'Message Test Conversation'
    })
    conv_data = json.loads(conv_response.data)['data']

    # Enviar mensaje
    response = client.post('/api/messages', json={
        'session_id': conv_data['id'],
        'user_id': user_data['id'],
        'content': 'Hello, AI!'
    })
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['success'] == True
    assert 'content' in data['data']
    assert 'response' in data['data']