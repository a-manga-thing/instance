from aiohttp.web import get, post, Response, json_response, HTTPBadRequest, HTTPForbidden
from aiohttp import FormData
from json import dumps, loads
from io import BytesIO

class NotAllowed(HTTPForbidden):
    def __init__(self, ip):
        super().__init__(text="Only localhost and whitelisted IP's can access the admin routes, Your IP: {}".format(ip))

class Routes:
    def __init__(self, instance):
        self.instance = instance
        self.instance.web.add_routes([
            post("/admin/add_manga", self.add_manga),
            post("/admin/add_chapter", self.add_chapter),
            post("/admin/add_scanlator", self.add_scanlator),
            post("/admin/rm_manga", self.rm_manga),
            post("/admin/rm_chapter", self.rm_chapter),
            get("/admin/subscribe", self.subscribe_to_instance),
            get("/admin/unsubscribe", self.unsubscribe_from_instance)
        ])

    def _check(self, request):
        addresses = ["127.0.0.1"] + self.instance.config.admin_ips
        if request.remote not in addresses:
            raise NotAllowed(request.remote)

    async def _post_async(self,form):
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
        res = (await res.text()).splitlines()
        try:
            return [loads(i) for i in res]
        except JSONDecodeError: 
            print("IPFS server error: ", res)
            return []
            

    async def add_manga(self, request):
        self._check(request)
        data = (await request.post()).copy()
        data["titles"] = [i.strip() for i in data["titles"].split(",")]
        data["artists"] = [i.strip() for i in data["artists"].split(",")]
        data["authors"] = [i.strip() for i in data["authors"].split(",")]
        data["genres"] = [i.strip() for i in data["genres"].split(",")]
        manga = await self.instance.db.create_manga(**data)
        return json_response({"id" : manga}, status=201)

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
        res = await self._post_async(form)
        if len(res) > 0:
            cid = next(i["Hash"] for i in res if not i["Name"])
            chapter = await self.instance.db.create_chapter(ipfs_link=cid, page_count=len(form) , **request.query)
            return json_response({"id" : chapter}, status=201)
        else:
            return Response(status=500)

    async def add_scanlator(self, request):
        self._check(request)
        data = await request.post()
        res = await self.instance.db.create_scanlator(**data)
        return json_response({"id" : res}, status=201)

    async def rm_manga(self, request):
        self._check(request)
        await self.instance.db.rm_manga(request.query.get("id"))

    async def rm_chapter(self, request):
        self._check(request)
        await self.instance.db.rm_chapter(request.query.get("id"))

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
