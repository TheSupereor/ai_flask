import sqlite3

def create_db():
    """Cria a tabela no banco de dados SQL se não existir"""
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            model TEXT,
            user_id INTEGER
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bot_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bot_id TEXT,
            url TEXT,
            content TEXT,
            UNIQUE(bot_id, url)  -- Garante que um usuário não salve o mesmo link duas vezes
        )
    """)
    conn.commit()
    conn.close()

create_db()

### Links

def get_saved_content(bot_id, url):
    """Verifica se o bot já tem um link específico salvo"""
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT content FROM bot_links WHERE bot_id = ? AND url = ?", (bot_id, url))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def save_content(bot_id, url, content):
    """Salva um link e seu conteúdo no banco, associa bot"""
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO bot_links (bot_id, url, content) VALUES (?, ?, ?)
    """, (bot_id, url, content))
    conn.commit()
    conn.close()
    
def get_bot_links_fromdb(bot_id):
    """Retorna todos os links salvos em um bot""" 
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT url, content FROM bot_links WHERE bot_id = ?", (bot_id))
    links = cursor.fetchall()
    conn.close()
    return [{"url": link[0], "content": link[1]} for link in links]
    
def get_bot(bot_id):
    """Retorna se um bot existe, se não existir, cria um"""
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, model FROM bots WHERE id = ?", (bot_id))
    bot = cursor.fetchone()
    if not bot: save_bot(bot_id, "")
    conn.commit()
    conn.close()
    return {"bot_id": bot[0], "name": bot[1], "model": bot[2]} if bot else None
    
def get_bots_from_user(user_id):
    """Lista todos os bots de um usuário"""
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, model FROM bots WHERE user_id = ?", (user_id))
    bots = cursor.fetchall()
    conn.commit()
    conn.close()
    return [{"url": bot[0], "content": bot[1]} for bot in bots]
    
def save_bot(name, model, user_id):
    """Cria um bot no banco"""
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO bots (name, model, user_id) VALUES (?, ?, ?)
    """, (name, model, user_id))
    conn.commit()
    conn.close()
    return "ok"