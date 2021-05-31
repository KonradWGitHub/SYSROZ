import MySQLdb
from datetime import datetime

MESSAGES_TABLE = "history"
USERS_TABLE = "users"

class Database:

    def connect(self):
        """
        try to connect to file and create cursor
        """
        cursor = self.connection.cursor(MySQLdb.cursors.DictCursor)
        return cursor

    def close(self):
        """
        close the db connection
        :return: None
        """
        self.connection.close()

    def get_all_messages(self, limit=100, name=None, to=None):
        """
        gets all messages sent and received
        :param limit: int
        :param name: str
        :param to: str
        :return: list(results)
        """
        cursor = Database.connect(self)
        query = f"SELECT * FROM {MESSAGES_TABLE} WHERE (name = %s AND recipient_name = %s) OR (name = %s AND recipient_name = %s)"
        cursor.execute(query, (name, to, to, name))
        result = cursor.fetchall()
        # return messages in sorted order by date
        results = []
        for r in result[:limit]:
            _id, content, name, to, date = r['history_id'], r['content'], r['name'], r['recipient_name'], r['time']
            data = {"from": name, "to": to, "message": content, "time": str(date)}
            results.append(data)
        return list(results)

    def save_message(self, msg, name, to, time):
        """
        saves the given message in the table
        :param name: str
        :param to: str
        :param msg: str
        :param time: datetime
        :return: None
        """
        cursor = Database.connect(self)
        query = f"INSERT INTO {MESSAGES_TABLE} (content, name, recipient_name, time) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (msg, name, to, time))
        self.connection.commit()

    def get_id(self, email):
        """
        gets user's room id
        :param email: str
        :return: my_id
        """
        cursor = Database.connect(self)
        query = f"SELECT username FROM {USERS_TABLE} WHERE email=%s"
        cursor.execute(query, (email,))
        username = cursor.fetchone()
        my_id = username['username']
        return my_id
