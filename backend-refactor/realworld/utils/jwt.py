import jwt
from datetime import datetime, timedelta
import os

SECRET_KEY = os.getenv("SECRET_KEY")


def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=15)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token
