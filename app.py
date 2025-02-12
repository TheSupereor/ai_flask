from flask import Flask
from flask_cors import CORS
from api import api_bp  # Importa o Blueprint definido em api/__init__.py

def initialize_app():
    app = Flask(__name__)
    CORS(app)

    # Registra as rotas da API com o prefixo /api
    app.register_blueprint(api_bp, url_prefix='/api')

initialize_app()
# if __name__ == "__main__":
#     app.run(port=5000, debug=True)
