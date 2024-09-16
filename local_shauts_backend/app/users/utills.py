import jwt
from datetime import datetime, timedelta, timezone
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


    
def serialized_user(user):
    return {
        'id': user.id,
        'role_id': user.role_id,
        'affilate_id': user.affilate_id,
        'name': user.name,
        'email': user.email,
        'profile_pic': user.profile_pic,
        'details': user.details,
        'created_at': user.created_at.strftime('%d-%m-%Y %I:%M%p'),
        'updated_at': user.updated_at.strftime('%d-%m-%Y %I:%M%p'),
        'timestamp': int(user.updated_at.replace(tzinfo=timezone.utc).timestamp()),
    } 
    
            


