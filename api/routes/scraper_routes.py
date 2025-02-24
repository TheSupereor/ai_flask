
from flask import Blueprint, jsonify, request

from api.services.scraper_service import extract_article_from_url, get_links_from_bot, save_from_url


scraper_bp = Blueprint("scraper", __name__)

@scraper_bp.route('/save_linkinfo', methods=['POST'])
def save_normal_content():
    """"Recebe uma lista de links e o bot_id, salvando o conteúdo no banco"""
    data = request.json
    links = data.get("links", [])
    bot = data.get("bot_id", "")

    if not links or not bot:
        return jsonify({"error": "Link e bot_id devem ser fornecidos"}), 400

    results = {link: save_from_url(bot, link) for link in links}
    if results.__contains__(Exception): return jsonify({"error": "houve um erro ao salvar os links"}), 400
    return jsonify({"message": "Links salvos!"})

@scraper_bp.route('/save_articleinfo', methods=['POST'])
def save_article_content():
    """"Recebe uma lista de links e o bot_id, salvando o conteúdo no banco"""
    data = request.json
    links = data.get("links", [])
    bot = data.get("bot_id", "")

    if not links or not bot:
        return jsonify({"error": "Link e bot_id devem ser fornecidos"}), 400

    results = {link: extract_article_from_url(bot, link) for link in links}
    return jsonify({"message": "Links salvos!"})

@scraper_bp.route('/get_bot_links', methods=['GET'])
def get_bot_links():
    """"Recebe o bot_id e retorna uma lista dos links salvos"""
    data = request.json
    bot = data.get("bot_id", "")

    if not bot:
        return jsonify({"error": "bot_id deve ser fornecido"}), 400

    results = get_links_from_bot(bot)
    return jsonify(results)