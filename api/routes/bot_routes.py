from flask import Blueprint, request, jsonify
from api.database.database import get_bot, get_bots_from_user, save_bot
from api.services.chromadb_service import search_documents
from api.services.ollama_service import generate_response
from api.services.scraper_service import search_in_links

bot_bp = Blueprint("bot", __name__)
DEFAULT_MODEL = "smollm:135m"

@bot_bp.route('/botcreate', methods=['POST'])
def create_bot():
    """"Cria um novo bot"""
    data = request.json
    name = data.get("name", "")
    user_id = data.get("user_id", "")
    model = data.get("model", DEFAULT_MODEL)
    
    if not model or not name or not user_id:
        return jsonify({"error": "name, user_id e model devem ser fornecidos"}), 400
    
    result = save_bot(name, model, user_id)
    return jsonify({"message": "bot criado com sucesso!"})

@bot_bp.route('/bot_list', methods=['POST'])
def get_bot_list():
    """"Obtém lista de bots de usuário"""
    data = request.json
    user_id = data.get("user_id", "")
    
    if not user_id:
        return jsonify({"error": "user_id deve ser fornecido"}), 400
    
    result = get_bots_from_user(user_id)
    return jsonify(result)

@bot_bp.route('/ask', methods=['POST'])
def ask():
    """Pergunta básica de prompt"""
    data = request.json
    model = data.get("model", DEFAULT_MODEL) 
    prompt = data.get("prompt", "")

    if not prompt:
        return jsonify({"error": "O prompt não pode estar vazio"}), 400

    response = generate_response(model, prompt)
    return jsonify(response)

@bot_bp.route('/ask_rag', methods=['POST'])
def ask_rag_doc():
    """Primeiro pergunta sem RAG. Se o modelo não souber, busca contexto externo."""
    data = request.json
    model = data.get("model", DEFAULT_MODEL)
    bot_id = data.get("bot_id", "")
    prompt = data.get("prompt", "")

    if not prompt or not bot_id:
        return jsonify({"error": "Nem o prompt nem o bot podem estar vazio"}), 400

    bot = get_bot(bot_id)
    if not bot:
        return jsonify({"error": "bot não encontrado"}), 400

    relevant_docs = search_documents(prompt, bot_id, top_k=3)
    context = "\n".join(relevant_docs) if relevant_docs else "Nenhuma informação relevante encontrada."

    full_prompt = f"Utilize essas informações como contexto: {context}\n\nRespondendo essa pergunta: {prompt}"
    final_response = generate_response(model, full_prompt)

    return jsonify({"response": final_response["response"], "source": "RAG"})

@bot_bp.route('/ask_with_links', methods=['POST'])
def ask_with_links():
    """Pergunta primeiro para a IA, e se necessário, busca em links""" 
    data = request.json
    model = data.get("model", DEFAULT_MODEL)
    prompt = data.get("prompt", "")
    bot_id = data.get("bot_id", "")
    links = data.get("links", [])

    if not prompt or not links:
        return jsonify({"error": "Prompt e links são obrigatórios"}), 400

    bot = get_bot(bot_id)
    if not bot:
        return jsonify({"error": "bot não encontrado"}), 400
    
    extracted_info = search_in_links(bot_id, prompt, links)

    if not extracted_info:
        return jsonify({"error": "Nenhuma informação útil encontrada nos links."})

    context = "\n".join(extracted_info)
    full_prompt = f"Baseado nessas fontes:\n{context}\n\nPergunta: {prompt}"

    final_response = generate_response(model, full_prompt)

    return jsonify({"response": final_response["response"], "source": "Links"})

