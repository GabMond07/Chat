from flask import Blueprint, request, jsonify
from core.chat_manager import ChatManager

chat_bp = Blueprint('chat', __name__)
chat_manager = ChatManager()

@chat_bp.route('/chat', methods=['POST'])
def chat():
    """
    Handle chat messages
    """
    data = request.get_json()
    response = chat_manager.process_message(data)
    return jsonify(response)