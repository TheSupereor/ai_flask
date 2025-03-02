import requests
import os

from huggingface_hub import InferenceClient


API_URL = "https://api-inference.huggingface.co/models/pierreguillou/gpt2-small-portuguese" 
HEADERS = {"Authorization": f"Bearer {os.getenv("HFTOKEN")}"}


def query_hf(prompt):
    try:
        client = InferenceClient(
            provider="hf-inference",
            api_key=os.getenv("HFTOKEN")
        )
        
        messages = [{
            "role": "user",
            "content": prompt
        }]
    
        completion = client.chat.completions.create(
            model="cnmoro/Qwen2.5-0.5B-Portuguese-v1",
            messages=messages,
            max_tokens=500,
        )
        
        return completion.choices[0].message;
    except:
        return "Não foi possível obter resposta da IA"
