from flask import Flask
from flask_cors import CORS
from api.routes import main_bp

app = Flask(__name__)
CORS(app)

# Registra as rotas da API com o prefixo /api
app.register_blueprint(main_bp)

# if __name__ == "__main__":
#     app.run(port=5000, debug=True)
