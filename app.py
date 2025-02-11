from flask import Flask, request, jsonify
import requests

AI_url = "http://localhost:11434"

app = Flask(__name__)

@app.route("/ask", methods=['POST'])
def ask():
    data = request.json
    prompt = data.get("prompt", "")
    
    if not prompt:
        return jsonify({"error": "O prompt não pode ser vazio"}), 400
    
    ask_AI_url = AI_url + "/api/generate"
    response = requests.post(ask_AI_url, json={
        "model": "mistral",
        "prompt": prompt,
        "stream": False
    })
    
    if response.status_code != 200:
        return jsonify({"error": "Erro ao se comunicar com a IA"}), 500
    
    return jsonify({"response": response.json()["response"]})
    
    
# if __name__ == "__main__":
#     app.run(port=5000, debug=True)
