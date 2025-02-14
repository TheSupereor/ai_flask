from flask import request, jsonify

from services.chromadb_service import add_document, search_documents
from services.scraper_service import extract_article_from_url, get_links_from_user, save_from_url, search_in_links
from services.ollama_service import generate_response
from . import api_bp  # Importa o Blueprint definido em __init__.py

DEFAULT_MODEL = "splitpierre/bode-alpaca-pt-br"
# smollm:135m

@api_bp.route('/save_linkinfo', methods=['POST'])
def save_normal_content():
    """"Recebe uma lista de links e o user_id, salvando o conteúdo no banco"""
    data = request.json
    links = data.get("links", [])
    user = data.get("user_id", "")

    if not links or not user:
        return jsonify({"error": "Link e user_id devem ser fornecidos"}), 400

    results = {link: save_from_url(link, user) for link in links}
    return jsonify({"message": "Links salvos!"})

@api_bp.route('/save_articleinfo', methods=['POST'])
def save_article_content():
    """"Recebe uma lista de links e o user_id, salvando o conteúdo no banco"""
    data = request.json
    links = data.get("links", [])
    user = data.get("user_id", "")

    if not links or not user:
        return jsonify({"error": "Link e user_id devem ser fornecidos"}), 400

    results = {link: extract_article_from_url(user, link) for link in links}
    return jsonify({"message": "Links salvos!"})

@api_bp.route('/save_articleinfo', methods=['GET'])
def get_user_links():
    """"Recebe o user_id e retorna uma lista dos links salvos"""
    data = request.json
    user = data.get("user_id", "")

    if not user:
        return jsonify({"error": "user_id deve ser fornecido"}), 400

    results = get_links_from_user(user)
    return jsonify(results)

@api_bp.route('/save_document', methods=['POST'])
def save_document():
    """Recebe um documento para salvar no banco, correlacionando com usuário"""
    data = request.json
    doc_id = data.get("id")
    text = data.get("text")
    user = data.get("user_id", "")
    metadata = {
        "user_id": user
    }

    if not doc_id or not text or not user:
        return jsonify({"error": "ID, user_id e texto são obrigatórios"}), 400

    add_document(doc_id, text, metadata)
    return jsonify({"message": "Documento adicionado com sucesso!"})

@api_bp.route('/ask', methods=['POST'])
def ask():
    """Pergunta básica de prompt"""
    data = request.json
    model = data.get("model", DEFAULT_MODEL) 
    prompt = data.get("prompt", "")

    if not prompt:
        return jsonify({"error": "O prompt não pode estar vazio"}), 400

    response = generate_response(model, prompt)
    return jsonify(response)

@api_bp.route('/ask_rag', methods=['POST'])
def ask_rag_doc():
    """Primeiro pergunta sem RAG. Se o modelo não souber, busca contexto externo."""
    data = request.json
    model = data.get("model", DEFAULT_MODEL)
    user_id = data.get("user_id", "")
    prompt = data.get("prompt", "")

    if not prompt or not user_id:
        return jsonify({"error": "Nem o prompt nem o user podem estar vazio"}), 400

    # 1️⃣ Pergunta sem contexto
    initial_response = generate_response(model, prompt)

    # 2️⃣ Se o modelo tem certeza, retornamos a resposta
    if initial_response["certainty"]:
        return jsonify({"response": initial_response["response"], "source": "IA sem RAG"})

    # 3️⃣ Se não tem certeza, busca no ChromaDB
    relevant_docs = search_documents(prompt, user_id, top_k=3)
    context = "\n".join(relevant_docs) if relevant_docs else "Nenhuma informação relevante encontrada."

    # 4️⃣ Pergunta novamente com contexto do RAG
    full_prompt = f"Contexto: {context}\n\nPergunta: {prompt}"
    final_response = generate_response(model, full_prompt)

    return jsonify({"response": final_response["response"], "source": "RAG"})

@api_bp.route('/ask_with_links', methods=['POST'])
def ask_with_links():
    ### Pergunta primeiro para a IA, e se necessário, busca em links
    data = request.json
    model = data.get("model", DEFAULT_MODEL)
    prompt = data.get("prompt", "")
    user_id = data.get("user_id", "")
    links = data.get("links", [])

    if not prompt or not links:
        return jsonify({"error": "Prompt e links são obrigatórios"}), 400

    # 1️⃣ Pergunta sem contexto
    initial_response = generate_response(model, prompt)

    if initial_response["certainty"]:
        return jsonify({"response": initial_response["response"], "source": "IA sem RAG"})

    # 2️⃣ Se a IA não tem certeza, busca nos links fornecidos pelo usuário
    extracted_info = search_in_links(user_id, prompt, links)

    if not extracted_info:
        return jsonify({"error": "Nenhuma informação útil encontrada nos links."})

    # 3️⃣ Monta um novo prompt com o conteúdo dos links
    context = "\n".join(extracted_info)
    full_prompt = f"Baseado nessas fontes:\n{context}\n\nPergunta: {prompt}"

    # 4️⃣ Pergunta para a IA novamente com contexto
    final_response = generate_response(model, full_prompt)

    return jsonify({"response": final_response["response"], "source": "Links"})

