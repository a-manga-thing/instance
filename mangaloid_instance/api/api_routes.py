from aiohttp.web import get, json_response, HTTPBadRequest

class InvalidInput(HTTPBadRequest):
    def __init__(self):
        super().__init__(text="You either did not provide a necessary parameter or it is of the wrong type")

class ApiRoutes:
    def __init__(self, instance):
        self.instance = instance
        self.instance.web.add_routes([
            get("/info", self.info),
            get("/manga/from_id", self.from_id),
            get("/manga/search", self.search),
            get("/manga/get_chapters", self.get_chapters),
            get("/manga/get_chapter", self.get_chapter),
            get("/manga/get_page", self.get_page)
        ])

    async def info(self, request):
        return json_response(self.instance.to_dict())

    async def from_id(self, request):
        try:
            query_id = int(request.query.get("id"))
        except Exception as e:
            raise InvalidInput()
        manga = await self.instance.db.get_manga_by_id(query_id)
        return json_response(manga.to_dict())

    async def search(self, request):
        title = request.query.get("query")
        creators = request.query.get("creators")
        if creators:
            creators = [i.lower().strip() for i in creators.split(",")]
        manga = await self.instance.db.search_by_title(title)
        if manga and creators:
            manga = [i for i in manga if [_.lower() for _ in i.creators] == creators]
        return json_response([i.to_dict() for i in manga])

    async def get_chapters(self, request):
        try:
            query_id = int(request.query.get("id"))
        except Exception as e:
            raise InvalidInput()
        chapters = await self.instance.db.get_chapters(query_id)
        return json_response([i.to_dict() for i in chapters])

    async def get_chapter(self, request):
        try:
            query_id = int(request.query.get("id"))
            number = float(request.query.get("number"))
        except Exception as e:
            raise InvalidInput()
        chapter = await self.instance.db.get_chapter(query_id, number)
        return json_response(chapter.to_dict())

    async def get_page(self, request):
        pass