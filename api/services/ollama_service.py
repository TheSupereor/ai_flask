import ollama
from pydantic import BaseModel
from api.database.database import get_bot
from api.services.chromadb_service import search_documents
from api.services.scraper_service import get_links_from_bot
#from typing import List

# class Button(BaseModel):
#     title: str
#     text: str

# class ListItem(BaseModel):
#     title: str
#     text: str

# class Response(BaseModel):
#     message: str
#     buttons: List[Button]
#     list: List[ListItem]

def generate_response(model: str, prompt: str):
    ### Gera uma resposta usando Ollama
    response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
    reply = response["message"]["content"]
    
    return {"response": reply}

def generate_response_based_bot(prompt: str, bot_id: str):
    ### Gera uma resposta usando ollama, obtendo os dados do bot via bot_id
    bot_data = get_bot(bot_id)
    print(bot_data)
    full_prompt = prompt
    
    relevant_docs = search_documents(prompt, bot_id, top_k=3)
    context = "\n".join(relevant_docs) 
    if relevant_docs:
        full_prompt += f"\n\nUsing the following content: {context}"
    else:
        print("Nenhuma informação relevante encontrada nos docs.")
    
    links = get_links_from_bot(bot_id)
    links_context = "\n".join(links)
    if links_context:
        full_prompt += f"\n\nUse these links and info: {links_context}"
    else:
        print("Nenhuma informação relevante encontrada nos links.")
        
    response = ollama.chat(
        model=bot_data["model"], 
        messages= [
                {"role": "user", "content": full_prompt}
            ],
        #format= Response.model_json_schema(),
        )
    #reply = Response.model_validate_json(response.message.content)
    reply = response["message"]["content"]
    print(reply)
    return {"response": reply}