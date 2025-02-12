from flask import Blueprint

# Cria o Blueprint da API
api_bp = Blueprint('api', __name__)

# Importa as rotas para registrar no Blueprint
from . import routes