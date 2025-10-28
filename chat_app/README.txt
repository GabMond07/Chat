# Chat IA - Aplicación con Arquitectura de Servicios

## 📋 Descripción

Aplicación de chat inteligente implementada siguiendo los patrones de arquitectura orientada a servicios:

- ✅ **Functional Decomposition**: Sistema dividido en funciones pequeñas y bien definidas
- ✅ **Service Encapsulation**: Cada servicio oculta su implementación interna
- ✅ **Agnostic Context**: Servicios reutilizables independientes de la infraestructura
- ✅ **Non-Agnostic Context**: Capa de transporte específica (Flask/HTTP)
- ✅ **Service Layers**: Organización en capas lógicas
- ✅ **Canonical Expression**: DTOs estandarizados para intercambio de datos

## 🏗️ Arquitectura

### Capas del Sistema

#### Capa 1: Servicios Agnósticos (Lógica de Negocio Reutilizable)

**Entity Services** - Operaciones CRUD sobre entidades:
- `UserService`: Gestión de usuarios (create, read, update, delete, authenticate)
- `MessageService`: Gestión de mensajes (create, read, update, delete, send)
- `ConversationService`: Gestión de conversaciones (create, read, update, delete)

**Utility Services** - Funciones de utilidad puras:
- `TextUtils`: Limpieza, sanitización, validación de texto
- `TimeUtils`: Manejo de timestamps y zonas horarias

**AI Service** - Servicio de Inteligencia Artificial:
- `AIService`: Consulta a modelos de lenguaje (queryAIModel, analyzeWithAI, predictIntent)

#### Capa 2: Task Services (Composición de Capacidades)

- `MessagingCapability`: Orquesta el flujo completo de mensajería
  - Combina UserService, MessageService, ConversationService
  - Valida entrada
  - Consulta IA
  - Guarda conversación
  - Devuelve respuesta

#### Capa 3: Servicios No Agnósticos (Transporte)

- `APIController`: Traduce HTTP/JSON a DTOs canónicos
- `ResponseHandler`: Formatea respuestas HTTP

### DTOs Canónicos

Todos los servicios usan DTOs estandarizados:
- `UserDTO`: Representación canónica de usuario
- `MessageDTO`: Representación canónica de mensaje
- `ConversationDTO`: Representación canónica de conversación
- `ResponseDTO`: Formato estándar de respuestas

## 📦 Instalación

### 1. Clonar o crear el proyecto

```bash
mkdir chat_app
cd chat_app
```

### 2. Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno (opcional)

Crear archivo `.env`:

```env
SECRET_KEY=tu-clave-secreta
DATABASE_URL=sqlite:///chat_app.db
AI_MODEL_NAME=microsoft/DialoGPT-medium
AI_MAX_LENGTH=1000
```

### 5. Ejecutar la aplicación

```bash
python app.py
```

La aplicación estará disponible en `http://localhost:5000`

## 🔌 API Endpoints

### Usuarios

#### Registrar Usuario
```http
POST /api/users/register
Content-Type: application/json

{
  "username": "usuario123",
  "email": "usuario@example.com",
  "password": "password123"
}
```

#### Login
```http
POST /api/users/login
Content-Type: application/json

{
  "username": "usuario123",
  "password": "password123"
}
```

#### Obtener Conversaciones de Usuario
```http
GET /api/users/1/conversations
```

### Conversaciones

#### Crear Conversación
```http
POST /api/conversations
Content-Type: application/json

{
  "user_id": 1,
  "title": "Mi primera conversación"
}
```

#### Obtener Historial de Conversación
```http
GET /api/conversations/1?user_id=1
```

### Mensajes

#### Enviar Mensaje
```http
POST /api/messages
Content-Type: application/json

{
  "user_id": 1,
  "session_id": 1,
  "content": "Hola, ¿cómo estás?"
}
```

Respuesta:
```json
{
  "success": true,
  "message": "Mensaje procesado exitosamente",
  "data": {
    "user_message": {
      "id": 1,
      "session_id": 1,
      "sender": "user",
      "content": "Hola, ¿cómo estás?",
      "timestamp": "2025-10-19T..."
    },
    "bot_message": {
      "id": 2,
      "session_id": 1,
      "sender": "bot",
      "content": "¡Hola! Estoy bien, gracias...",
      "timestamp": "2025-10-19T..."
    }
  }
}
```

### Salud del Servicio

```http
GET /api/health
```

## 🧪 Flujo de Ejemplo

### 1. Registrar Usuario

```bash
curl -X POST http://localhost:5000/api/users/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test_user","email":"test@example.com","password":"pass123"}'
```

### 2. Crear Conversación

```bash
curl -X POST http://localhost:5000/api/conversations \
  -H "Content-Type: application/json" \
  -d '{"user_id":1,"title":"Primera conversación"}'
```

### 3. Enviar Mensaje

```bash
curl -X POST http://localhost:5000/api/messages \
  -H "Content-Type: application/json" \
  -d '{"user_id":1,"session_id":1,"content":"Hola bot!"}'
```

### 4. Ver Historial

```bash
curl http://localhost:5000/api/conversations/1?user_id=1
```

## 🎯 Principios Implementados

### Functional Decomposition
Cada función tiene una responsabilidad única y está bien definida.

### Service Encapsulation
La lógica interna está oculta detrás de interfaces claras. Puedes cambiar:
- El proveedor de IA sin modificar MessagingCapability
- La base de datos sin modificar los controladores
- El framework web sin modificar los servicios agnósticos

### Agnostic Context
Los servicios agnósticos no dependen de:
- Flask
- HTTP
- WebSocket
- Ningún protocolo de transporte

Pueden reutilizarse en:
- CLI
- API REST
- WebSocket
- Aplicación móvil
- Microservicios

### Service Layers
Tres capas claras:
1. **Agnóstica**: Lógica de negocio reutilizable
2. **Task Services**: Composición de capacidades
3. **No Agnóstica**: Transporte e infraestructura

### Canonical Expression
Todos los servicios usan convenciones estándar:
- CRUD: create, read (get), update, delete
- DTOs canónicos para intercambio
- Formato de respuesta estandarizado

## 📊 Base de Datos

### Entidades

**User**
- id (PK)
- username (unique)
- email (unique)
- password_hash
- created_at
- is_active

**Session**
- id (PK)
- user_id (FK → User)
- title
- created_at
- updated_at
- is_active

**ChatMessage**
- id (PK)
- session_id (FK → Session)
- sender ('user' | 'bot')
- content
- timestamp
- is_edited

## 🔒 Validaciones

- Longitud de mensaje: 1-500 caracteres (configurable)
- Sanitización de entrada (elimina caracteres peligrosos)
- Verificación de contenido ofensivo
- Autenticación de usuario
- Autorización por sesión

## 🚀 Próximos Pasos

Para completar la aplicación según el documento:
1. Implementar frontend (interfaz de usuario)
2. Agregar WebSocket para chat en tiempo real
3. Implementar sistema de notificaciones
4. Agregar más validaciones y filtros
5. Implementar caché para respuestas frecuentes
6. Agregar logging y monitoreo
7. Implementar rate limiting

## 📝 Notas Importantes

- El modelo de IA se carga al iniciar la aplicación (puede tardar)
- La primera respuesta puede ser lenta mientras se carga el modelo
- SQLite se usa por defecto (cambiar a PostgreSQL/MySQL en producción)
- Las contraseñas se hashean con bcrypt

## 🐛 Troubleshooting

**Error al cargar modelo:**
- Verifica conexión a internet
- El modelo se descarga la primera vez
- Puede requerir varios GB de espacio

**Base de datos no se crea:**
- Verifica permisos de escritura
- Elimina `chat_app.db` y reinicia

**Respuestas lentas:**
- Normal en primera ejecución
- Considera usar un modelo más pequeño
- En producción, usar GPU