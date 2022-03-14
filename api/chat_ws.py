import asyncio
import websockets
import json
from asgiref.sync import sync_to_async
from api.models import *
from jwt_auth.models import *
from jwt_auth.auth import check_token
from threading import Thread
from datetime import datetime
from django.conf import settings


async def message_router(websocket):
    data = json.loads(await websocket.recv())
    profile = await sync_to_async(check_token)(data["token"])
    while not profile or profile == "expired":
        await websocket.send(json.dumps({"message": "invalid token"}))
        data = json.loads(await websocket.recv())
    await websocket.send(json.dumps({"message": "ok"}))
    messages = await sync_to_async(set)(await sync_to_async(Message.objects.filter)(to_profile=profile))
    deals = await sync_to_async(set)(await sync_to_async(Deal.objects.filter)(owner=profile))
    while True:
        updated_messages = await sync_to_async(set)(await sync_to_async(Message.objects.filter)(to_profile=profile))
        updated_deals = await sync_to_async(set)(await sync_to_async(Deal.objects.filter)(owner=profile))
        if messages != updated_messages:
            new = sorted(await sync_to_async(list)(updated_messages.difference(messages)), key=lambda msg: msg.sent)
            messages = updated_messages
            get_from_id = lambda msg: msg.from_profile.id
            get_to_id = lambda msg: msg.to_profile.id
            new = [{
                "from": await sync_to_async(get_from_id)(msg),
                "to": await sync_to_async(get_to_id)(msg),
                "text": msg.text,
                "sent": msg.sent.timestamp()
            } for msg in new]
            await websocket.send(json.dumps({"messages": new}))
        if deals != updated_deals:
            new = updated_deals.difference(deals)
            deals = updated_deals
            new = [
                await sync_to_async(lambda deal: {"deal_id": deal.id, "car_id": deal.car.id, "amount": deal.amount, "sender": deal.cliend.id})(deal)
                for deal in new
            ]
            await websocket.send(json.dumps({"deals": new}))
        await asyncio.sleep(1)

    

async def main():
    async with websockets.serve(message_router, settings.HOST, 8765, ping_interval=None):
        await asyncio.Future()

def run_ws():
    asyncio.run(main())
