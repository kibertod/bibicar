import jwt

from datetime import datetime, timedelta
from api.models import *
from jwt_auth.models import *
from django.contrib.auth import authenticate
from django.conf import settings


def generate_jwt_tokens(profile):
    dt = datetime.now() + timedelta(days=1)

    token = jwt.encode({
        'id': profile.id,
        'exp': int(dt.strftime('%s'))
    }, settings.SECRET_KEY, algorithm='HS256')

    refresh = jwt.encode({
        'id': profile.id,
        'token_data': {
            'id': profile.id,
            'exp': int(dt.strftime('%s'))
        }
    }, settings.SECRET_KEY, algorithm='HS256')

    SessionToken.objects.create(profile=profile, token=token, refresh=refresh)
    return {"token": token, "refresh_token": refresh, "id": profile.id}


def check_token(token):
    try:
        data = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
    except:
        return "expired"
    if SessionToken.objects.filter(token=token):
        return SessionToken.objects.get(token=token).profile
    else:
        return False


def logout(token):
    if SessionToken.objects.filter(token=token):
        SessionToken.objects.get(token=token).delete()
        return True
    else:
        return False
