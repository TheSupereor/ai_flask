from flask import request, jsonify

from api.services.chromadb_service import add_document, search_documents
from .services.ollama_service import generate_response
from . import api_bp  # Importa o Blueprint definido em __init__.py

@api_bp.route('/add_document', methods=['POST'])
def add_document_route():
    data = request.json
    doc_id = data.get("id")
    text = data.get("text")
    metadata = data.get("metadata", {})

    if not doc_id or not text:
        return jsonify({"error": "ID e texto são obrigatórios"}), 400

    add_document(doc_id, text, metadata)
    return jsonify({"message": "Documento adicionado com sucesso!"})

@api_bp.route('/ask', methods=['POST'])
def ask():
    data = request.json
    model = data.get("model", "smollm:135m") 
    prompt = data.get("prompt", "")

    if not prompt:
        return jsonify({"error": "O prompt não pode estar vazio"}), 400

    response = generate_response(model, prompt)
    return jsonify(response)

@api_bp.route('/ask_rag', methods=['POST'])
def ask_smart():
    """Primeiro pergunta sem RAG. Se o modelo não souber, busca contexto externo."""
    data = request.json
    model = data.get("model", "mistral")
    prompt = data.get("prompt", "")

    if not prompt:
        return jsonify({"error": "O prompt não pode estar vazio"}), 400

    # 1️⃣ Pergunta sem contexto
    initial_response = generate_response(model, prompt)

    # 2️⃣ Se o modelo tem certeza, retornamos a resposta
    if initial_response["certainty"]:
        return jsonify({"response": initial_response["response"], "source": "IA"})

    # 3️⃣ Se não tem certeza, busca no ChromaDB
    relevant_docs = search_documents(prompt, top_k=3)
    context = "\n".join(relevant_docs) if relevant_docs else "Nenhuma informação relevante encontrada."

    # 4️⃣ Pergunta novamente com contexto do RAG
    full_prompt = f"Contexto: {context}\n\nPergunta: {prompt}"
    final_response = generate_response(model, full_prompt)

    return jsonify({"response": final_response["response"], "source": "RAG"})