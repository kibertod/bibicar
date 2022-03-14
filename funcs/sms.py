def send_sms(message, phone):
    return None
    credentials = {
            "grant_type": "client_credentials",
            "client_id": settings.SENDPULSE_ID,
            "client_secret": settings.SENDPULSE_SECRET
        }
    access_token = json.loads(requests.post("https://api.sendpulse.com/oauth/access_token", data=credentials).text)["access_token"]
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    data = {
        "sender":"Bibicar",
        "phones":[
            phone,
        ],
        "body":message,
        "transliterate":0,
        "route":{
            "UA":"sim_ua",
            "RU":"sim_ru"
        },
        "emulate":1,
        "date":str(datetime.now().replace(microsecond=0) + timedelta(seconds=5))
    }
    print(data)
    url = "https://api.sendpulse.com/sms/send"
    res = json.loads(requests.post(url, headers=headers, data=data).text)
    print(res)