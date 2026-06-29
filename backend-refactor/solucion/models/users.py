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
    def _query_user(field, value):
        try:
            result = couchbase_db.query(f'SELECT * FROM `users` WHERE {field} = "{value}"')
            for row in result.rows():
                user_data = row["users"]
                if user_data:
                    return User(
                        user_data["user_id"], user_data["username"],
                        user_data["email"], user_data["password"]
                    )
            return None
        except CouchbaseException as e:
            print(f"Couchbase query error on {field}={value}: {e}")
            return None

    @staticmethod
    def get_user_by_id(user_id):
        return User._query_user("user_id", user_id)

    @staticmethod
    def get_by_username(username):
        return User._query_user("username", username)

    @staticmethod
    def get_by_email(email):
        return User._query_user("email", email)

    def delete(self):
        couchbase_db.delete_document("users", str(self.user_id))
