from aiohttp.web import get

class ApiRoutes:
    def __init__(self, instance):
        self.instance = instance
        self.instance.web.add_routes([
            get("/from_id", self.from_id),
            get("/search", self.search),
            get("/get_chapter", self.get_chapter),
            get("/get_page", self.get_page)
        ])

    async def from_id(self, request):
        pass

    async def search(self, request):
        pass
    
    async def get_chapter(self, request):
        pass

    async def get_page(self, request):
        pass