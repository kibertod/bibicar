from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.core.files.base import ContentFile
from django.shortcuts import render
from django.contrib.auth.models import User
from django.conf import settings
from django.core.files import File
from django.core.mail import send_mail
from django.core.files.temp import NamedTemporaryFile
from django.contrib.auth.hashers import make_password, check_password

from datetime import datetime, timedelta
import jwt
from uuid import uuid4
import requests
import vk_api
import json
import secrets
import string
import base64

from api.views import error_callback, get_profile_data
from jwt_auth.auth import logout, check_token, generate_jwt_tokens
from jwt_auth.models import *
from funcs.sms import *
    

@csrf_exempt
@error_callback
def register(request):
    data = json.loads(request.body)

    user_data = dict()

    if "email" in data.keys():
        if Profile.objects.filter(email=data["email"]):
            return JsonResponse({'error': 'email already in use'}, status=505)
        user_data["email"] = data["email"]

    if "phone" in data.keys():
        if Profile.objects.filter(phone=data["phone"]):
            return JsonResponse({'error': 'phone already in use'}, status=505)
        user_data["phone"] = data["phone"]
    
    if data["phone_notification"] == True and not "phone" in data.keys():
        return JsonResponse({'error': 'supply phone number to use phone notification'}, status=505)
    
    if data["email_notification"] == True and not "email" in data.keys():
        return JsonResponse({'error': 'supply email address to use email notification'}, status=505)

    if "image" in data.keys():
        format, imgstr = data["image"].split(';base64,') 
        ext = format.split('/')[-1] 
        user_data["image"] = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
    if "passport" in data.keys():
        user_data["passport"] = data["passport"]
    if "license" in data.keys():
        user_data["license"] = data["license"]
    if "first_name" in data.keys():
        user_data["first_name"] = data["first_name"]
    if "middle_name" in data.keys():
        user_data["middle_name"] = data["middle_name"]
    if "last_name" in data.keys():
        user_data["last_name"] = data["last_name"]
    user_data["password"] = make_password(data["password"])

    code = "1234" # ''.join(secrets.choice(string.digits) for i in range(4))
    token = uuid4()
    while RegTemp.objects.filter(token=token):
        token = uuid4()
    user_data["token"] = token
    user_data["code"] = code

    if data["email_notification"]:
        send_mail(
            'Подтверждение аккаунта',
            f'Введите этот код в приложении: {code}',
            settings.EMAIL_HOST_USER,
            [data["email"]],
            fail_silently=False,
        )
    elif data["phone_notification"]:
        send_sms(f"Подтверждение регистрации. Введите этот код в приложении: {code}", data["phone"])
    else:
        JsonResponse({"chose at least one notification type": token})

    RegTemp.objects.create(**user_data)

    return JsonResponse({"check_token": token})


@csrf_exempt
@error_callback
def send_reg_code_again(request):
    data = json.loads(request.body)

    token = data["check_token"]
    if not RegTemp.objects.filter(token=token):
        return JsonResponse({"error": "invalid token"}, status=404)

    temp = RegTemp.objects.get(token=token)
    if temp.email_notification:
        send_mail(
            'Подтверждение аккаунта',
            f'Введите этот код в приложении: {temp.code}',
            settings.EMAIL_HOST_USER,
            [temp.email],
            fail_silently=True,
        )
    elif temp.email_notification:
        send_sms(f"Подтверждение регистрации\nВведите этот код в приложении: {temp.code}", temp.phone)

    return JsonResponse({"message": "ok"})


@csrf_exempt
@error_callback
def register_confirm(request):
    data = json.loads(request.body)

    token = data["check_token"]
    if not RegTemp.objects.filter(token=token):
        return JsonResponse({"error": "invalid token"}, status=404)

    temp = RegTemp.objects.get(token=token)

    if not data["code"] == temp.code:
        return JsonResponse({"error": "invalid code"}, status=505)
    
    profile = Profile.objects.create(email=temp.email, password=temp.password,
        first_name=temp.first_name, last_name=temp.last_name, middle_name=temp.middle_name,
        image=temp.image, passport=temp.passport, phone=temp.phone
    )

    tokens = generate_jwt_tokens(profile)
    return JsonResponse(tokens)
    



@csrf_exempt
@error_callback
def login_view(request):
    data = json.loads(request.body)

    if not Profile.objects.filter(email=data["email"]):
        return JsonResponse({'error': 'wrong data'}, status=505)

    profile = Profile.objects.get(email=data["email"])

    if not check_password(data["password"], profile.password):
        return JsonResponse({'error': 'wrong password'}, status=505)

    tokens = generate_jwt_tokens(profile)
    return JsonResponse(tokens)


@csrf_exempt
@error_callback
def logout_view(request):
    data = json.loads(request.body)
    logout(data["token"])
    return JsonResponse({"status": "ok"})


@csrf_exempt
@error_callback
def refresh(request):
    data = json.loads(request.body)
    if SessionToken.objects.filter(token=data["token"], refresh=data["refresh_token"]):
        session = SessionToken.objects.get(token=data["token"], refresh=data["refresh_token"])
        profile = session.profile
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
        session.token=token 
        session.refresh=refresh
        session.save()
        OldToken.objects.create(token=data["token"])
        return JsonResponse({"token": token, "refresh_token": refresh})
    else:
        if SessionToken.objects.filter(token=data["token"]):
            return JsonResponse({"error": "wrong refresh token"})
        elif OldToken.objects.filter(token=data["token"]):
            profile_id = jwt.decode(data["token"], settings.SECRET_KEY, algorithms='HS256', options={"verify_signature": False})["id"]
            profile = Profile.objects.get(id=profile_id)
            for session in SessionToken.objects.filter(profile=profile):
                session.delete()
            return JsonResponse({"error": "suspicious activity detected, relogin required"})
        else:
            return JsonResponse({"error": "wrong token"})


@csrf_exempt
def vk_auth(request):
    data = json.loads(request.body)

    if Profile.objects.filter(vk_id=data["id"]):
        profile = Profile.objects.get(vk_id=data["id"])
        message = "Вы авторизованы как"
    else:
        password = ''.join(secrets.choice(string.digits + string.ascii_letters) for i in range(10))

        profile = Profile.objects.create(password=make_password(password),
        first_name=data["first_name"], last_name=data["last_name"])

        if "email" in data.keys():
            profile.email = data["email"]
        else:
            data["email"] = ""
        if "photo" in data.keys():
            r = requests.get(data["photo"])
            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(r.content)
            img_temp.flush()
        profile.image = File(img_temp)
        profile.vk_id = data["id"]
        profile.save()
        message = "Аккаунт успешно создан"

    
    if not "email" in data.keys():
            data["email"] = ""
    
    return JsonResponse(generate_jwt_tokens(profile))


@csrf_exempt
def facebook_auth(request):
    data = json.loads(request.body)
    access_token = data["token"]

    app_token = json.loads(requests.get(f"https://graph.facebook.com/oauth/access_token?client_id={settings.FACEBOOK_ID}&client_secret={settings.FACEBOOK_SECRET}&grant_type=client_credentials").text)["access_token"]
    id = json.loads(requests.get(f"https://graph.facebook.com/debug_token?input_token={access_token}&access_token={app_token}").text)['data']['user_id']
    res = json.loads(requests.get(f"https://graph.facebook.com/{id}/?fields=first_name,last_name,picture.type(large),email&access_token={access_token}").text)
    if Profile.objects.filter(fb_id=id):
        profile = Profile.objects.get(fb_id=id)
        message = "Вы авторизованы как"
    else:
        password = ''.join(secrets.choice(string.digits + string.ascii_letters) for i in range(10))

        profile = Profile.objects.create(password=make_password(password),
        first_name=res["first_name"], last_name=res["last_name"])

        if "email" in res.keys():
            profile.email = res["email"]
        else:
            res["email"] = "Почта не указана"
        if "picture" in res.keys():
            if "url" in res["picture"]["data"].keys():
                r = requests.get(res["picture"]["data"]["url"])
                img_temp = NamedTemporaryFile(delete=True)
                img_temp.write(r.content)
                img_temp.flush()
                profile.image = File(img_temp)
        profile.fb_id = id
        profile.save()
        message = "Аккаунт успешно создан"

    if not "email" in res.keys():
        res["email"] = "Почта не указана"
    
    return JsonResponse(generate_jwt_tokens(profile))
