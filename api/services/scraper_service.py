import requests
from bs4 import BeautifulSoup
from newspaper import Article

from api.database.database import get_bot_links_fromdb, get_saved_content, save_content

def save_from_url(bot_id, url):
    """Busca o conteúdo salvo ou faz scraping"""
    print(bot_id)
    print(url)
    saved_content = get_saved_content(bot_id, url)
    if saved_content:
        print(f"🔹 Conteúdo já salvo {url} do usuário {bot_id}")
        return saved_content

    try:
    ### Obtem dados
        article = Article(url)
        article.download()
        article.parse()
        content = article.text

        save_content(bot_id, url, content)  # Salva para o usuário
        return content
    except Exception as e:
        print(f"Erro ao processar {url}: {e}")
        return e

def extract_article_from_url(bot_id: str, url: str):
    """Baixa o artigo e extrai o conteúdo principal"""
    # 1️⃣ Verifica se o link já está no banco
    saved_content = get_saved_content(bot_id, url)
    if saved_content:
        print(f"🔹 Usando conteúdo salvo para {url}")
        return saved_content
    
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        content = soup.get_text()

        # 3️⃣ Salva no banco para uso futuro
        save_content(bot_id, url, content)
        return content
    except Exception as e:
        print(f"Erro ao processar {url}: {e}")
        return None

def search_in_links(bot_id: str, query, links):
    """Pesquisa os links e retorna apenas os trechos que contêm o termo da busca"""
    results = []
    for link in links:
        text = save_from_url(bot_id, link)  # Obtém o texto do link
        if not text:
            continue

        # Busca trechos que contêm o termo
        lower_text = text.lower()
        lower_query = query.lower()
        if lower_query in lower_text:
            sentences = text.split(". ")  # Divide o texto em frases
            matching_sentences = [s for s in sentences if lower_query in s.lower()]
            result_text = " [...] ".join(matching_sentences[:5])  # Pega trechos

            results.append(f"🔎 **Resultado encontrado:**\n📌 **Fonte:** {link}\n📄 **Trecho:** {result_text}\n")
    
    return results if results else ["Nenhum resultado relevante encontrado."]

def get_links_from_bot(bot_id: str):
    """Obtém links salvos de usuário"""
    try:
        links = get_bot_links_fromdb(bot_id)
        return links
    except Exception as e:
        print(f"Erro ao obter links de usuário {bot_id}")
        return None