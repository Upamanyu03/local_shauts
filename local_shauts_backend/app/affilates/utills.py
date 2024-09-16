from app.affilates.models import Affilate
from app.affilates.schemas import affilate_schema
from datetime import  timezone

def serialized_affilate(affilate, date):
    # date = {
    #         'sub_start': date.get('sub_start', ""),
    #         'sub_end': date.get('sub_end', ""),
    #     }
    return {
        'id': affilate.id,
        'affilate_name': affilate.affilate_name,
        'email': affilate.email,
        'mobile_number': affilate.mobile_number,
        'address': affilate.address,
        'sub_start': date.get('sub_start', ""),
        'sub_end': date.get('sub_end', ""),
        # 'affilate_logo': affilate.affilate_logo,
        'created_at': affilate.created_at.strftime('%d-%m-%Y %I:%M%p'),
        'updated_at': affilate.updated_at.strftime('%d-%m-%Y %I:%M%p'),
        'timestamp': int(affilate.updated_at.replace(tzinfo=timezone.utc).timestamp()),
        'deleted_at': affilate.deleted_at.strftime('%d-%m-%Y %I:%M%p')
    }