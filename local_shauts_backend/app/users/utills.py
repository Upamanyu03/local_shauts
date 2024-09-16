import jwt
from datetime import datetime, timedelta
import os
import pytz

def generate_token(user_id, days=365):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=days)
    }
    token = jwt.encode(payload, os.getenv('JWT_SECRET'), algorithm='HS256')
    return token    


def asia_kokata_time():
    utc_now = datetime.now(pytz.utc)
    asia_kolkata_timezone = pytz.timezone('Asia/Kolkata')
    return utc_now.astimezone(asia_kolkata_timezone)
