from flask import Blueprint
from .bot_routes import bot_bp
from .scraper_routes import scraper_bp
from .upload_routes import upload_bp

# Criamos um Blueprint principal para agrupar todas as rotas
main_bp = Blueprint("main", __name__)

# Registramos os blueprints individuais
main_bp.register_blueprint(bot_bp, url_prefix="/api")
main_bp.register_blueprint(scraper_bp, url_prefix="/api")
main_bp.register_blueprint(upload_bp, url_prefix="/api")
