import sqlite3

def get_user(user_id):
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    res = conn.execute(f'SELECT * FROM users WHERE id = {user_id} LIMIT 1').fetchone()
    conn.close()
    if not res:
        print('User not found')
        return False
    return res

class UserLogin():
    def fromDB(self, user_id):
        self.__user = get_user(user_id)
        return self
    
    def create(self, user):
        self.__user = user
        return self
    
    def is_authenticated(self):
        return True
    
    def is_active(self):
        return True
    
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.__user['id'])
    
    def get_name(self):
        return self.__user['name'] if self.__user else 'Not name'

    def get_email(self):
        return self.__user['email'] if self.__user else 'Not email'
    