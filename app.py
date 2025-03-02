import threading
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

from api.helpers.rabbitmqConnection import start_rpc_server
from api.routes import main_bp

app = Flask(__name__)
CORS(app)

# Registra as rotas da API com o prefixo /api
app.register_blueprint(main_bp)

# Inicia um thread para o rabbitmq
rpc_thread = threading.Thread(target=start_rpc_server)
rpc_thread.daemon = True  # Garante que a thread será finalizada junto com o app
rpc_thread.start()

if __name__ == "__main__":
    app.run(debug = True)
#     app.run(port=5000, debug=True)
