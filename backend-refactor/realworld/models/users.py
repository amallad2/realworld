import bcrypt
from extensions import couchbase_db
from couchbase.exceptions import CouchbaseException


class User:
    def __init__(self, user_id, username, email, password):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password = password

    def to_json(self):
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "password": self.password
        }

    def save(self):
        hashed_password = bcrypt.hashpw(self.password.encode('utf-8'), bcrypt.gensalt())
        self.password = hashed_password.decode('utf-8')
        couchbase_db.insert_document("users", str(self.user_id), self.to_json())

    @staticmethod
    def get_user_by_id(user_id):
        try:
            user_document = couchbase_db.query(f'SELECT * FROM `users` WHERE user_id = "{user_id}"')
            for row in user_document.rows():
                user_data = row["users"]
                if user_data:
                    return User(user_data["user_id"], user_data["username"], user_data["email"], user_data["password"])
            return None
        except CouchbaseException as e:
            print(f"### CouchbaseException: {e}")
            return None

    @staticmethod
    def get_by_username(username):
        try:
            user_document = couchbase_db.query(f'SELECT * FROM `users` WHERE username = "{username}"')
            for row in user_document.rows():
                user_data = row["users"]
                if user_data:
                    return User(user_data["user_id"], user_data["username"], user_data["email"], user_data["password"])
            return None
        except CouchbaseException as e:
            print(f"### CouchbaseException: {e}")
            return None

    @staticmethod
    def get_by_email(email):
        try:
            user_document = couchbase_db.query(f'SELECT * FROM `users` WHERE email = "{email}"')
            for row in user_document.rows():
                user_data = row["users"]
                if user_data:
                    return User(user_data["user_id"], user_data["username"], user_data["email"], user_data["password"])
            return None
        except CouchbaseException as e:
            print(f"### CouchbaseException: {e}")
            return None

    def delete(self):
        couchbase_db.delete_document("users", str(self.user_id))
