from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id):
        self.id = id
        self.name = "user"
        self.password = "qwerty"

    def get_id(self):
        return self.id


def get_user(user_id):
    if user_id == "1":
        return User(id="1")
    return None

def authenticate(username, password):
    if username == "user" and password == "qwerty":
        return User(id="1")
    return None
