from aiohttp.web import get, post, Response, json_response, HTTPBadRequest, HTTPForbidden

class NotAllowed(HTTPForbidden):
    def __init__(self):
        super().__init__(text="Only localhost and whitelisted IP's can access the admin routes")

class Routes:
    def __init__(self, instance):
        self.instance = instance
        self.instance.web.add_routes([
            post("/admin/add_manga", self.add_manga),
            post("/admin/add_chapter", self.add_chapter),
            get("/admin/subscribe", self.subscribe_to_instance),
            get("/admin/unsubscribe", self.unsubscribe_from_instance)
        ])

    def _check(self, request):
        addresses = ["127.0.0.1"] + self.instance.config.admin_ips
        print(addresses)
        if request.remote not in addresses:
            raise NotAllowed()

    async def add_manga(self, request):
        self._check(request)
        data = await request.post()
        manga = await self.instance.db.create_manga(**data)
        return json_response(manga.to_dict(), status=201)

    async def add_chapter(self, request):
        self._check(request)
        #TODO: Implement image verification and IPFS uploading
        data = await request.post()
        manga_id = data.get("manga_id")
        await self.instance.db.get_manga_by_id(manga_id)
        """
        form = await request.multipart()
        while True:
            part = await form.next()
            if part is None:
                break
            raw = await part.read()
            await self.instance.client.post("/api/v0/add", params={

            })
        """
        chapter = await self.instance.db.create_chapter(manga_id, **data)
        return json_response(chapter.to_dict(), status=201)

    async def subscribe_to_instance(self, request):
        self._check(request)
        address = request.query.get("address")
        res = await self.instance.client.get(params={"address" : self.instance.config.instance_address})
        if res.status == 200:
            self.instance.context["subscribe_confirmations"].append(address)
            return Response(body="Pending confirmation")
        return Response("The instance did not accept our request: '{}'".format(await res.text()))

    async def unsubscribe_from_instance(self, request):
        self._check(request)
        pass