from aiohttp.web import get, static, json_response, HTTPBadRequest, HTTPFound
from os import path

class InvalidInput(HTTPBadRequest):
    def __init__(self):
        super().__init__(text="You either did not provide a necessary parameter or it is of the wrong type")

class TooManyTags(HTTPBadRequest):
    def __init__(self):
        super().__init__(text="You can only have max {} genres".format(self.instance.config.max_tags))

class Routes:
    def __init__(self, instance):
        self.instance = instance
        self.instance.web.add_routes([
            get("/manga", self.from_id),
            get("/chapter", self.get_chapters),
            get("/search", self.search),
            get("/people", self.get_people),
            get("/scanlator", self.get_scanlators),
            get("/thumbnail", self.thumbnail),
            static("/thumb", self.instance.config.thumbnail_path)
        ])

    async def from_id(self, request):
        try:
            query_id = int(request.query.get("id"))
        except Exception:
            raise InvalidInput()
        manga = await self.instance.db.get_manga_by_id(query_id)
        return json_response(manga.to_dict())

    async def search(self, request):
        title = request.query.get("title")
        author = request.query.get("author")
        artist = request.query.get("artist")
        genres = request.query.get("genres")
        sort = request.query.get("sort")
        desc = "desc" in request.query
        try:
            limit = min(int(request.query.get("limit", self.instance.config.max_results)), self.instance.config.max_results)
            page = int(request.query.get("page", 0))
        except Exception:
            raise InvalidInput()
        if genres:
            genres = [i.strip() for i in genres.split(",")]
            if len(genres) > self.instance.config.max_tags:
                raise TooManyTags()
        manga = await self.instance.db.search(title=title, author=author, artist=artist, tags=genres, limit=limit, page=page, sortby=sort, descending=desc)
        return json_response([i.to_dict() for i in manga])

    async def get_chapters(self, request):
        try:
            query_id = int(request.query.get("id"))
        except Exception:
            raise InvalidInput()
        chapters = await self.instance.db.get_chapters(query_id)
        return json_response([i.to_dict() for i in chapters])

    async def thumbnail(self, request):
        try:
            query_id = int(request.query.get("id"))
        except Exception:
            raise InvalidInput()
        raise HTTPFound("/thumb/{}.webp".format(query_id))

    async def get_people(self, request):
        return json_response([i.name for i in await self.instance.db.get_people()])
    
    async def get_scanlators(self, request):
        return json_response([i.to_dict() for i in await self.instance.db.get_scanlators()])
