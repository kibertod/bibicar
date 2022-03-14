from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from django.core import serializers
from django.contrib.auth.models import User
from api.models import *
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password

from datetime import datetime, date, timedelta
import base64
import jwt
from uuid import uuid4
import random
import json
import vk_api
import string
import secrets
from requests import get, post

from jwt_auth.models import *
from jwt_auth.auth import logout, check_token, generate_jwt_tokens
from api.chat_ws import run_ws
from threading import Thread
from funcs.sms import *


bot = vk_api.VkApi(token=settings.VK_BOT_TOKEN)
t = Thread(target=run_ws)
t.setDaemon(True)
t.start()

def login_required(func, *args,**kwargs):
    def responce(*args, **kwargs):
        data = json.loads(args[0].body)
        if not "token" in data.keys():
            return JsonResponse({"error": "login required"}, status=505)
        elif OldToken.objects.filter(token=data["token"]):
            profile_id = jwt.decode(data["token"], settings.SECRET_KEY, algorithms='HS256')["id"]
            profile = Profile.objects.get(id=profile_id)
            for session in SessionToken.objects.filter(profile=profile):
                session.delete()
            return JsonResponse({"error": "suspicious activity detected, relogin required"},status=505)
        elif check_token(data["token"]) == "expired":
            return JsonResponse({"error": "need to refresh the token"}, status=505)
        elif not check_token(data["token"]):
            return JsonResponse({"error": "invalid token"}, status=505)
        else:
            return func(*args,**kwargs)
    return responce


def error_callback(func, *args, **kwargs):
    def responce(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            e = str(e)
            res = {'error': e}
            return JsonResponse(res, status=500)
    return responce

@csrf_exempt
def load_cars(request):
    with open("csv.csv", "r") as file:
        models = [ model.rstrip("\n").split(";") for model in file.readlines()]
    for model in models:
        if not Mark.objects.filter(name=model[0]):
            Mark(name=model[0]).save()
            print(model[0])
        end_year = model[3]
        if end_year == "-":
            end_year = None
        Model(mark=Mark.objects.get(name=model[0]),
              name=model[1],
              start_year=model[2],
              end_year=end_year).save()
        print(f"{model[0]} - {model[1]}")
    return HttpResponse("success")


@csrf_exempt
@error_callback
def get_marks(request):
    res = [{
        "id": mark.id,
        "name": mark.name
    } for mark in Mark.objects.all()]
    res = {
        "marks": res
    }
    return JsonResponse(res)


@csrf_exempt
@error_callback
def get_models(request):
    data = json.loads(request.body)
    res = [{
        "id": model.id,
        "name": model.name,
        "mark": model.mark.name,
        "years": list(range(model.start_year, model.end_year + 1)) if model.end_year\
                     else list(range(model.start_year, datetime.now().year + 1))
    } for model in Model.objects.filter(mark=Mark.objects.get(id=data["mark_id"]))]
    res = {
        "models": res
    }
    return JsonResponse(res)


@csrf_exempt
def get_cars(request):
    data = json.loads(request.body)
    res = []
    filters = dict()
    if "city" in data.keys():
        filters["city"] = data["city"]
    if "district" in data.keys():
        filters["district"] = data["district"]
    if "street" in data.keys():
        filters["street"] = data["street"]
    if "term" in data.keys():
        filters["term"] = data["term"]
    if "carcase" in data.keys():
        filters["carcase"] = data["carcase"]
    if "class" in data.keys():
        filters["_class"] = data["class"]
    
    if not filters:
        cars = Car.objects.all()
    else:
        cars = Car.objects.filter(**filters)
    
    if "prices" in data.keys():
        cars = filter(lambda car: data["prices"][0] <= car.price <= data["prices"][1], cars)

    if "years" in data.keys():
        cars = filter(lambda car: data["years"][0] <= car.year <= data["years"][1], cars)

    if "start_date" in data.keys():
        swap = []
        for car in cars:
            if not car.end_date:
                swap.append(car)
            elif car.start_date <= datetime.fromisoformat(data["start_date"]).date() <= car.end_date:
                swap.append(car)
        cars = swap
    
    if "end_date" in data.keys():
        swap = []
        for car in cars:
            if not car.end_date:
                swap.append(car)
            elif car.start_date <= datetime.fromisoformat(data["end_date"]).date() <= car.end_date:
                swap.append(car)
        cars = swap

    for param in ["engine", "power", "drive", "color", "mileage", "rudder"]:
        if param not in data.keys():
            data[param] = ""

    if "model" in data.keys():
        cars = filter(lambda car: len(set(f"{car.mark} {car.model}".lower().split()) & set(data["model"].lower().split())) >= 1, cars)
        key=lambda car: (car.engine==data["engine"],
                car.power==data["power"],
                car.frive==data["drive"],
                car.color==data["color"],
                car.mileage==data["mileage"],
                car.rudder==data["rudder"],
                len(set(f"{car.mark} {car.model}".lower().split()) & set(data["model"].lower().split())) -
                len(set(f"{car.mark} {car.model}".lower().split()) | set(data["model"].lower().split())))
        cars = sorted(cars, key=key, reverse=True)


    res = []
    for car in json.loads(serializers.serialize("json", cars)):
        print(car)
        res.append(car["fields"])
        res[-1]["images"] = []
        res[-1]["id"] = car["pk"]
        for image in CarImage.objects.filter(car=Car.objects.get(id=car["pk"])):
            res[-1]["images"].append(image.image.url)
    res = {
        "cars": res
    }
    return JsonResponse(res)


@csrf_exempt
def view_car(request):
    data = json.loads(request.body)
    car = json.loads(serializers.serialize("json", Car.objects.filter(id=data["id"])))[0]
    car_model = Car.objects.get(id=data["id"])
    car_model.views += 1
    car_model.save()
    res = car["fields"]
    res["id"] = data["id"]
    res["images"] = []
    for image in CarImage.objects.filter(car=Car.objects.get(id=data["id"])):
            res["images"].append(image.image.url)
    return JsonResponse({"car": res})

def get_profile_data(profile):
    if profile.image:
        image = profile.image.url
    else:
        image = None
    res = {
        "first_name": profile.first_name,
        "middle_name": profile.middle_name,
        "last_name": profile.last_name,
        "email": profile.email,
        "phone": profile.phone,
        "passport": profile.passport,
        "license": profile.license,
        "image": image,
        "vk_integrated": bool(profile.vk_id),
        "created": profile.created,
        "cars": []
    }

    rating = len(set([profile.first_name, profile.last_name, profile.middle_name, profile.vk_id, profile.email, profile.phone,
              profile.passport, profile.image])) / 8 * 100
    res["rating"] = rating

    res["reviews"] = {
        "from": [],
        "to": []
    }

    for review in Review.objects.filter(target=profile):
        res["reviews"]["to"].append({
            "author": {
                "first_name": review.author.first_name,
                "middle_name": review.author.middle_name,
                "last_name": review.author.last_name,
                "id": review.author.id
            },
            "text": review.text,
            "is_positive": review.is_positive
        })
    for review in Review.objects.filter(author=profile):
        res["reviews"]["from"].append({
            "target": {
                "first_name": review.target.first_name,
                "middle_name": review.target.middle_name,
                "last_name": review.target.last_name,
                "id": review.target.id
            },
            "text": review.text,
            "is_positive": review.is_positive
        })
    
    res["favorites"] = []
    for favorite in Favorite.objects.filter(profile=profile):
        res["favorites"].append(favorite.car.id)
    
    for car in json.loads(serializers.serialize("json", Car.objects.filter(owner=profile))):
        res["cars"].append(car["fields"])
        res["cars"][-1]["images"] = []
        for image in CarImage.objects.filter(car=Car.objects.get(id=car["pk"])):
            res["cars"][-1]["images"].append(image.image.url)

    return res


@csrf_exempt
@error_callback
def get_profile(request):
    data = json.loads(request.body)

    profile = Profile.objects.get(id=data["id"])
    return JsonResponse(get_profile_data(profile))


@csrf_exempt
@error_callback
@login_required
def add_favorite(request):
    data = json.loads(request.body)
    profile = check_token(data["token"])

    car = Car.objects.get(data["car_id"]).id
    Favorite.objects.create(profile=profile, car=car)
    return JsonResponse({"message": "ok"})


@csrf_exempt
@error_callback
@login_required
def del_favorite(request):
    data = json.loads(request.body)
    profile = check_token(data["token"])

    car = Car.objects.get(data["car_id"]).id
    Favorite.objects.get(profile=profile, car=car).delete()
    return JsonResponse({"message": "ok"})


@csrf_exempt
@error_callback
@login_required
def update_profile(request):
    data = json.loads(request.body)
    profile = check_token(data["token"])
    updates = dict()
    if "image" in data.keys():
        format, imgstr = data["image"].split(';base64,') 
        ext = format.split('/')[-1] 
        profile.image = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
    if "passport" in data.keys():
        profile.passport = data["passport"]
    if "phone" in data.keys():
        profile.phone = data["phone"]
    if "license" in data.keys():
        profile.license = data["license"]
    if "first_name" in data.keys():
        profile.first_name = data["first_name"]
    if "middle_name" in data.keys():
        profile.middle_name = data["middle_name"]
    if "last_name" in data.keys():
        profile.last_name = data["last_name"]

    profile.save()
    return JsonResponse(get_profile_data(profile))


@csrf_exempt
@error_callback
@login_required
def delete_profile(request):
    data = json.loads(request.body)
    profile = check_token(data["token"])
    profile.delete()
    return JsonResponse({"message": "ok"})


@csrf_exempt
@error_callback
@login_required
def add_car(request):
    data = json.loads(request.body)
    profile = check_token(data["token"])

    if not profile.ads and not profile.vip_till:
        return JsonResponse({"error": "no ads"}, status=505)
    
    if not date.today() > profile.vip_till:
        if not profile.ads:
            return JsonResponse({"error": "no ads"}, status=505)
        profile.ads -= 1

    profile.save()

    if not "district" in data.keys():
        data["district"] = None
    if not "end_date" in data.keys():
        data["end_date"] = None
    
    for param in ["engine", "power", "drive", "color", "mileage", "rudder"]:
        if param not in data.keys():
            data[param] = ""
    
    car = Car.objects.create(
        mark=data["mark"],
        owner=profile,
        city=data["city"],
        district=data["district"],
        street=data["street"],
        model=data["model"],
        year=data["year"],
        start_date=data["start_date"],
        end_date=data["end_date"],
        term=data["term"],
        carcase=data["carcase"],
        _class=data["class"],
        price=data["price"],
        engine=data["engine"],
        power=data["power"],
        drive=data["drive"],
        color=data["color"],
        mileage=data["mileage"],
        rudder=data["rudder"],
        )
    
    res = {
        "car": json.loads(serializers.serialize("json", Car.objects.filter(id=car.id)))[0]["fields"]
    }

    res["car"]["images"] = []

    if "images" in data.keys():
        for image in data["images"]:
            format, imgstr = image.split(';base64,') 
            ext = format.split('/')[-1]
            car_image = CarImage.objects.create(image=ContentFile(base64.b64decode(imgstr), name='temp.' + ext),
                car=car
            )
            res["car"]["images"].append(car_image.image.url)
    
    return JsonResponse(res)


@csrf_exempt
@error_callback
@login_required
def extend_car_ad(request):
    data = json.loads(request.body)
    profile = check_token(data["token"])
    car = Car.objects.get(id=data["id"])
    price = Settings.objects.get(key="AD_PRICE").value
    if profile.balance < price:
        return JsonResponse({"error": "low balance"}, status=505)
    elif profile != car.owner:
        return JsonResponse({"error": "wrong profile"}, status=505)
    else:
        profile.balance -= price
        car.active_till += date.toady() + timedelta(months=1)
        profile.save()
        car.save()
    return JsonResponse({"message": "success"})


@csrf_exempt
@error_callback
@login_required
def boost_car(request):
    data = json.loads(request.body)
    profile = check_token(data["token"])
    car = Car.objects.get(id=data["id"])
    price = Settings.objects.get(key="BOOST_PRICE").value
    if profile.balance < price:
        return JsonResponse({"error": "low balance"}, status=505)
    elif profile != car.owner:
        return JsonResponse({"error": "wrong profile"}, status=505)
    else:
        profile.balance -= price
        car.boosted_till += date.toady() + timedelta(months=1)
        profile.save()
        car.save()
    return JsonResponse({"message": "success"})


@csrf_exempt
@error_callback
@login_required
def add_review(request):
    data = json.loads(request.body)

    author = check_token(data["token"])
    target = Profile.objects.get(id=data["target_id"])
    text = data["text"]
    is_positive = data["is_positive"]

    review = Review.objects.create(author=author, target=target, text=text, is_positive=is_positive)
    
    res = {
        "author": {
            "id": author.id,
            "email": author.email,
            "first_name": author.first_name,
            "middle_name": author.middle_name,
            "last_name": author.last_name,
        },
        "target": {
            "id": target.id,
            "email": target.email,
            "first_name": target.first_name,
            "middle_name": target.middle_name,
            "last_name": target.last_name,
        },
        "text": text,
        "is_positive": is_positive,
        "created": review.created
    }

    return JsonResponse(res)


@csrf_exempt
@error_callback
def reset_password(request):
    data = json.loads(request.body)

    code = ''.join(secrets.choice(string.digits) for i in range(4))
    token = uuid4()
    while ChangePasswordTemp.objects.filter(token=token):
        token = uuid4()
    
    password = make_password(data["password"])

    if data["identifier"]["type"] == "phone":
        if not Profile.objects.filter(phone=data["identifier"]["value"]):
            return JsonResponse({"error": "doesn't exist"}, status=500)
        profile = Profile.objects.get(phone=data["identifier"]["value"])
    if data["identifier"]["type"] == "email":
        if not Profile.objects.filter(email=data["identifier"]["value"]):
            return JsonResponse({"error": "doesn't exist"}, status=500)
        profile = Profile.objects.get(email=data["identifier"]["value"])

    
    if data["identifier"]["type"] == "email":
        send_mail("Смена пароля", code, settings.EMAIL_HOST_USER, [profile.email])
        ChangePasswordTemp.objects.create(token=token, profile=profile, code=code, new_password=password, confirmation_type="email")
    else:
        send_sms(code, profile.phone)
        ChangePasswordTemp.objects.create(token=token, profile=profile, code=code, new_password=password, confirmation_type="phone")
    
    return JsonResponse({"check_token": token})



@csrf_exempt
@error_callback
def change_password(request):
    data = json.loads(request.body)
    profile = check_token(data["token"])

    code = ''.join(secrets.choice(string.digits) for i in range(4))
    token = uuid4()
    while ChangePasswordTemp.objects.filter(token=token):
        token = uuid4()
    
    password = make_password(data["password"])

    if data["notification"] == "email":
        send_mail("Смена пароля", code, settings.EMAIL_HOST_USER, [profile.email])
        ChangePasswordTemp.objects.create(token=token, profile=profile, code=code, new_password=password, confirmation_type="email")
    else:
        send_sms(code, profile.phone)
        ChangePasswordTemp.objects.create(token=token, profile=profile, code=code, new_password=password, confirmation_type="phone")
    

    
    return JsonResponse({"check_token": token})


@csrf_exempt
@error_callback
def change_password_confirm_resend(request):
    data = json.loads(request.body)
    token = data["check_token"]

    if ChangePasswordTemp.objects.filter(token=token):
        temp = ChangeEmailTemp.objects.get(token=token)
        profile = temp.profile
        if temp.confirmation_type == "email":
            send_mail("Смена пароля", temp.code, settings.EMAIL_HOST_USER, [profile.email])
        else:
            send_sms(temp.code, profile.phone)
        send_mail("Смена пароля", temp.code, settings.EMAIL_HOST_USER, [profile.email])
        
        return JsonResponse({"message": "ok"})
    else:
        return JsonResponse({"error": "invalid check token"})


@csrf_exempt
@error_callback
def change_password_confirm(request):
    data = json.loads(request.body)
    token = data["check_token"]
    code = data["code"]

    if ChangePasswordTemp.objects.filter(token=token, code=code):
        profile = ChangePasswordTemp.objects.get(token=token).profile
        profile.password = ChangePasswordTemp.objects.get(token=token).new_password
        profile.save()

        for session in SessionToken.objects.filter(profile=profile):
            session.delete()
        
        return JsonResponse(generate_jwt_tokens(profile))
    elif ChangePasswordTemp.objects.filter(token=token):
        return JsonResponse({"error": "invalid code"})
    else:
        return JsonResponse({"error": "invalid check token"})


@csrf_exempt
@login_required
@error_callback
def change_email(request):
    data = json.loads(request.body)
    profile = check_token(data["token"])
    email = data["email"]

    if Profile.objects.filter(email=email):
        return JsonResponse({'error': 'email already in use'}, status=505)

    code = ''.join(secrets.choice(string.digits) for i in range(4))
    token = uuid4()
    while ChangeEmailTemp.objects.filter(token=token):
        token = uuid4()

    ChangeEmailTemp.objects.create(code=code, profile=profile, token=token, email=email)

    send_mail("Смена электронной почты", code, settings.EMAIL_HOST_USER, [email])

    return JsonResponse({"check_token": token})


@csrf_exempt
@login_required
@error_callback
def change_email_confirm_resend(request):
    data = json.loads(request.body)
    profile = check_token(data["token"])
    token = data["check_token"]

    if ChangeEmailTemp.objects.filter(profile=profile, token=token):
        temp = ChangeEmailTemp.objects.get(profile=profile, token=token)

        send_mail("Смена электронной почты", temp.code, settings.EMAIL_HOST_USER, [temp.email])
        
        return JsonResponse({"message": "ok"})
    else:
        return JsonResponse({"error": "invalid check token"})


@csrf_exempt
@login_required
@error_callback
def change_email_confirm(request):
    data = json.loads(request.body)
    profile = check_token(data["token"])
    token = data["check_token"]
    code = data["code"]

    if ChangeEmailTemp.objects.filter(profile=profile, token=token, code=code):
        profile.email = ChangeEmailTemp.objects.get(profile=profile, token=token, code=code).email
        profile.save()

        for session in SessionToken.objects.filter(profile=profile):
            session.delete()
        
        return JsonResponse(generate_jwt_tokens(profile))
    elif ChangeEmailTemp.objects.filter(profile=profile, token=token):
        return JsonResponse({"error": "invalid code"})
    else:
        return JsonResponse({"error": "invalid check token"})


    return JsonResponse({"check_token": token})


@csrf_exempt
@login_required
@error_callback
def send_message(request):
    data = json.loads(request.body)
    from_profile = check_token(data["token"])
    to_profile = Profile.objects.get(id=data["to_id"])
    text = data["text"]
    Message.objects.create(from_profile=from_profile, to_profile=to_profile, text=text)
    return JsonResponse({"message": "ok"})


@csrf_exempt
@login_required
@error_callback
def get_messages(request):
    data = json.loads(request.body)
    profile = check_token(data["token"])

    res = {
        "chats": []
    }
    partners = dict()

    for msg in Message.objects.filter(to_profile=profile.id):
        if msg.from_profile not in partners.keys():
            partners[msg.from_profile.id] = []
        partners[msg.from_profile.id].append({
            "from": msg.from_profile.id,
            "to": msg.to_profile.id,
            "text": msg.text,
            "sent": msg.sent.timestamp()
        })
    for msg in Message.objects.filter(from_profile=profile.id):
        if msg.to_profile not in partners.keys():
            partners[msg.to_profile.id] = []
        partners[msg.to_profile.id].append({
            "from": msg.from_profile.id,
            "to": msg.to_profile.id,
            "text": msg.text,
            "sent": msg.sent.timestamp()
        })
        
    for partner in partners.keys():
        messages = partners[partner]
        partner = Profile.objects.get(id=partner)
        res["chats"].append({
            "partner": {
                "id": partner.id,
                "first_name": partner.first_name,
                "last_name": partner.last_name,
                "image": partner.image.url
            },
            "messages": messages
        })

    return JsonResponse(res)


def get_lists(request):
    res = [list.name for list in List.objects.all()]
    return JsonResponse({"lists": res})

def get_list_values(request, list_name):
    res = [item.value for item in ListItem.objects.filter(list=List.objects.get(name=list_name))]
    return JsonResponse({"values": res})

@csrf_exempt
@login_required
@error_callback
def deposit(request):
    data = json.loads(request.body)
    profile = check_token(data["token"])
    token = str(uuid4())
    payload = {
            "id": token,
            "amount": {
                "currency": "RUB"
            },
            "test": True,
            "description": "Пополнение счёта Bibicar",
            "projectCode": "cybertoad.ru",
            "sender": {
                "name": f"{profile.first_name} {profile.last_name}",
                "phone": profile.phone,
                "email": profile.email,
            },
            "successUrl": "https://cybertoad.ru",
            "failUrl": "https://cybertoad.ru"
        }
    headers = {
        "Authorization": settings.CAPUSTA_TOKEN,
        "Content-Type": "application/json"
    }
    Payment.objects.create(token=token, profile=profile)
    res = json.loads(post("https://api.capusta.space/v1/partner/payment", data=json.dumps(payload), headers=headers).text)
    return JsonResponse({"url": res["payUrl"]})


@csrf_exempt
def сallback(request):
    data = json.loads(request.body)
    token = data["transactionId"]
    if request.headers.get("Authorization") == settings.CAPUSTA_TOKEN and data["status"] == "SUCCESS":
        payment = Payment.objects.get(token=token)
        profile = payment.profile
        profile.balance += data["amount"]["amount"] // 100
        profile.save()
    return HttpResponse("ok")


@csrf_exempt
@login_required
@error_callback
def get_vip(request):
    data = json.loads(request.body)
    profile = check_token(data["token"])
    if "months" in data.keys():
        months = data["months"]
    else:
        months = 1
    price = Settings.objects.get(key="VIP_PRICE_PER_MONTH").value * months
    if profile.balance < price:
        return JsonResponse({"error": "low balance"}, status=505)
    else:
        profile.balance -= price
        profile.vip_till = datetime.date.toady() + timedelta(months=months)
        profile.save()
        return JsonResponse({"message": "succes"})


@csrf_exempt
@login_required
@error_callback
def get_ads(request):
    data = json.loads(request.body)
    profile = check_token(data["token"])
    if "count" in data.keys():
        count = data["count"]
    else:
        count = 1
    price = Settings.objects.get(key="AD_PRICE").value * count
    if profile.balance < price:
        return JsonResponse({"error": "low balance"}, status=505)
    else:
        profile.balance -= price
        profile.ads = count
        profile.save()
        return JsonResponse({"message": "succes"})


@csrf_exempt
@error_callback
def get_prices(request):
    data = {
        "ad": Settings.objects.get(key="AD_PRICE"),
        "boost": Settings.objects.get(key="BOOST_PRICE"),
        "vip": Settings.objects.get(key="VIP_PRICE_PER_MONTH")
    }
    return JsonResponse(data)


@csrf_exempt
@login_required
@error_callback
def send_deal(request):
    data = json.loads(request.body)
    profile = check_token(data["token"])
    car = Car.objects.get(id=data["car_id"])
    owner = car.owner
    amount = data["amount"]
    Deal.objects.create(client=profile, car=car, amount=amount, owner=owner)
    return JsonResponse({"message": "success"})
