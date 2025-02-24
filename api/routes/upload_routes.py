

from flask import Blueprint, jsonify, request

from api.database.database import get_bot
from api.services.chromadb_service import add_document

upload_bp = Blueprint("upload", __name__)

@upload_bp.route('/save_document', methods=['POST'])
def save_document():
    """Recebe um documento para salvar no banco, correlacionando com usuário"""
    data = request.json
    doc_id = data.get("id")
    text = data.get("text")
    bot_id = data.get("bot_id", "")
    metadata = {
        "bot_id": bot
    }

    if not doc_id or not text or not bot_id:
        return jsonify({"error": "ID, bot_id e texto são obrigatórios"}), 400

    bot = get_bot(bot_id)
    if not bot:
        return jsonify({"error": "bot não encontrado"}), 400
    
    add_document(doc_id, text, metadata)
    return jsonify({"message": "Documento adicionado com sucesso!"})