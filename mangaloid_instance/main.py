from aiohttp.web import Application as HTTP
from asyncio import get_event_loop

from config import config
from storage import database
from models import instance
from api import api_routes

class Application(instance.Instance):
    def __init__(self):
        self.web = HTTP()
        self.db = database.Database(config.database)
        super().__init__(
            config.instance_name,
            config.instance_operator,
            config.instance_icon,
            config.instance_description
        )

    async def main(self):
        await self.db.init()
        api_routes.ApiRoutes(self)


get_event_loop().run_until_complete(Application().main())