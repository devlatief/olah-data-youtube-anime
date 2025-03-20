import sqlite3

def init_db():
    conn = sqlite3.connect('youtube_analytics.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS channels
        (channel_id TEXT PRIMARY KEY,
         channel_name TEXT,
         description TEXT)
    ''')
    conn.commit()
    conn.close()

def add_channel(channel_id, channel_name, description):
    conn = sqlite3.connect('youtube_analytics.db')
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO channels VALUES (?, ?, ?)',
              (channel_id, channel_name, description))
    conn.commit()
    conn.close()

def get_all_channels():
    conn = sqlite3.connect('youtube_analytics.db')
    c = conn.cursor()
    c.execute('SELECT * FROM channels')
    channels = c.fetchall()
    conn.close()
    return channels

def delete_channel(channel_id):
    conn = sqlite3.connect('youtube_analytics.db')
    c = conn.cursor()
    c.execute('DELETE FROM channels WHERE channel_id = ?', (channel_id,))
    conn.commit()
    conn.close()