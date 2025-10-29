import socketio
import time

sio = socketio.Client(logger=False, engineio_logger=False)

@sio.event
def connect():
    print('connected')
    sio.emit('join', {'user_id': 1, 'session_id': 1})
    time.sleep(0.2)
    sio.emit('message', {'user_id': 1, 'session_id': 1, 'content': 'Hello'})

@sio.on('new_message')
def on_new_message(data):
    print('new_message:', data)

@sio.on('error')
def on_error(data):
    print('error:', data)

@sio.event
def disconnect():
    print('disconnected')

if __name__ == '__main__':
    sio.connect('http://localhost:5000')
    sio.wait()
