import sqlite3
import datetime


class History:

    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)

    def get_chat_history(self, chat_id):
        cursor = self.conn.cursor()
        rows = cursor.execute('SELECT * FROM Messages WHERE chatname = ? ORDER BY timestamp', (chat_id,))
        messages = [msg_factory(cursor, row) for row in rows]
        return messages


def msg_factory(cursor, row):
    msg = {}
    for idx, col in enumerate(cursor.description):
        msg[col[0]] = row[idx]

    msg['created'] = datetime.datetime.fromtimestamp(msg['timestamp'])

    return msg
