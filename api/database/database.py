import sqlite3

def create_db():
    """Cria a tabela no banco de dados SQL se não existir"""
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            url TEXT,
            content TEXT,
            UNIQUE(user_id, url)  -- Garante que um usuário não salve o mesmo link duas vezes
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            title TEXT,
            content TEXT
        )
    """)
    conn.commit()
    conn.close()

create_db()

### Links

def get_saved_content(user_id, url):
    """Verifica se o usuário já tem um link específico salvo"""
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT content FROM user_links WHERE user_id = ? AND url = ?", (user_id, url))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def save_content(user_id, url, content):
    """Salva um link e seu conteúdo no banco, associa usuário"""
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO user_links (user_id, url, content) VALUES (?, ?, ?)
    """, (user_id, url, content))
    conn.commit()
    conn.close()
    
def get_user_links_fromdb(user_id):
    """Retorna todos os links salvos por um usuário""" 
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT url, content FROM user_links WHERE user_id = ?", (user_id))
    links = cursor.fetchall()
    conn.close()
    return [{"url": link[0], "content": link[1]} for link in links]
    
