from aiohttp.web import get, post, json_response
from .utils import get_key_pair, get_sync_payload
from ..storage.models import manga, chapter

sync_types = {"Manga" : manga.Manga, "Chapter" : chapter.Chapter}

class Routes:
    def __init__(self, manager):
        self.manager = manager
        self.manager.instance.web.add_routes([
            get("/sync/subscribe", self.subscribe),
            get("/sync/accept", self.accept),
            post("/sync/push", self.sync)
        ])

    async def subscribe(self, request):
        address = request.query.get("address", "")
        if address.endswith("/"):
            address = address[:-1]
        try:
            res = await self.manager.client.get("{}/sync/accept", params={"address" : self.manager.address})
            if res.status == 200:
                dc = await res.json()
                self.manager.db.add_manager(**dc)
                return json_response({"message" : "OK"}, status=201)
            return json_response({"message" : "The manager did not accept our subscription: {}".format(await res.text())}, status=403)
        except ConnectionError:
            return json_response({"message" : "Could not connect to the manager"}, status=400)

    async def accept(self, request):
        address = request.query.get("address")
        if address and address in self.manager.context["subscribe_confirmations"]:
            private, public = await get_key_pair()
            self.manager.db.add_subscription(address, private, public)
            dc = self.manager.instance.to_dict()
            dc["public_key"] = public
            self.manager.context["subscribe_confirmations"].remove(address)
            return json_response(dc)
        return json_response({"message" : "Not expecting subscription from this address"}, status=403)

    async def sync(self, request):
        dc = await request.json()
        subscription = await self.manager.db.get_subscription(dc["manager"])
        payload = await get_sync_payload(dc["payload"], subscription.private_key)