import ollama

UNCERTAINTY_KEYWORDS = ["não sei", "não tenho certeza", "não encontrei", "não possuo informação"]  

def generate_response(model: str, prompt: str):
    ### Gera uma resposta usando Ollama
    response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
    reply = response["message"]["content"]

    ### Se a IA demonstrar incerteza, acionar o RAG
    if any(keyword in reply.lower() for keyword in UNCERTAINTY_KEYWORDS):
        return {"response": reply, "certainty": False}  # Indica que pode precisar do RAG
    
    return {"response": reply, "certainty": True}