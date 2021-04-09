from aiohttp.web import get, post, Response, json_response
from aiohttp import ClientConnectionError
from .utils import get_key_pair, get_sync_payload

class Routes:
    def __init__(self, instance):
        self.instance = instance
        self.instance.web.add_routes([
            get("/sync/subscribe", self.subscribe),
            get("/sync/accept", self.accept),
            post("/sync/push", self.sync)
        ])

    async def subscribe(self, request):
        address = request.query.get("address", "")
        if address.endswith("/"):
            address = address[:-1]
        try:
            res = await self.instance.client.get("{}/sync/accept", params={"address" : self.instance.address})
            if res.status == 200:
                dc = await res.json()
                self.instance.db.add_instance(**dc)
                return json_response({"message" : "OK"}, status=201)
            return json_response({"message" : "The instance did not accept our subscription: {}".format(await res.text())}, status=403)
        except ConnectionError:
            return json_response({"message" : "Could not connect to the instance"}, status=400)

    async def accept(self, request):
        address = request.query.get("address")
        if address and address in self.instance.context["subscribe_confirmations"]:
            private, public = await get_key_pair()
            self.instance.db.add_subscription(address, private, public)
            dc = self.instance.to_dict()
            dc["public_key"] = public
            self.instance.context["subscribe_confirmations"].remove(address)
            return json_response(dc)
        return json_response({"message" : "Not expecting subscription from this address"}, status=403)

    async def sync(self, request):
        raise NotImplementedError() #TODO: Implement
        dc = await request.json()
        subscription = await self.instance.db.get_subscription(dc["instance"])
        payload = await get_sync_payload(dc["payload"], subscription.private_key)