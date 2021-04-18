from aiohttp.web import get, post, Response, json_response, HTTPBadRequest, HTTPForbidden
from aiohttp import FormData
from json import dumps, loads
from io import BytesIO

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
        if request.remote not in addresses:
            raise NotAllowed()

    async def post_async(self,form):
        data = FormData()
        for i in form:
            data.add_field("file", i, filename=i.name)
        res = await self.instance.client.post("{}/api/v0/add".format(self.instance.config.upload_ipfs_node),
            headers={"Accept" : "application/json"},
            data=data,
            params={
                "wrap-with-directory" : "true",
                "stream-channels" : "true",
                "pin" : "true",
                "quieter" : "true"
            })
        return [loads(i) for i in (await res.text()).splitlines()]

    async def add_manga(self, request):
        self._check(request)
        data = (await request.post()).copy()
        data["titles"] = [i.strip() for i in data["titles"].split(",")]
        data["artists"] = [i.strip() for i in data["artists"].split(",")]
        data["authors"] = [i.strip() for i in data["authors"].split(",")]
        data["genres"] = [i.strip() for i in data["genres"].split(",")]
        manga = await self.instance.db.create_manga(**data)
        return json_response(manga.to_dict(), status=201)

    async def add_chapter(self, request):
        self._check(request)
        #TODO: Implement image verification
        await self.instance.db.get_manga_by_id(request.query.get("manga_id"))
        reader = await request.multipart()
        form = []
        while True:
            part = await reader.next()
            if not part:
                break
            name = part.filename.split("/")[-1]
            data = BytesIO(await part.read())
            data.name = name
            form.append(data)
        res = await self.post_async(form)
        cid = next(i["Hash"] for i in res if not i["Name"])
        chapter = await self.instance.db.create_chapter(ipfs_link=cid, page_count=len(form) , **request.query)
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