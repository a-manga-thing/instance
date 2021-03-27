from aiohttp.web import Application as HTTP
from aiohttp.web import _run_app
from asyncio import get_event_loop

from config import config
from storage import database
from models import instance
from api import api_routes

class Application(instance.Instance):
    def __init__(self):
        self.web = HTTP()
        self.web.on_startup.append(self._background)
        self.db = database.Database(config.database)
        super().__init__(
            config.instance_name,
            config.instance_operator,
            config.instance_icon,
            config.instance_description
        )

    async def _background(self, app):
        pass

    async def _main(self):
        await self.db.init()
        api_routes.ApiRoutes(self)
        return await _run_app(self.web, host="0.0.0.0", port=config.http_port)

    def start(self):
        return get_event_loop().run_until_complete(self._main())

if __name__ == '__main__':
    Application().start()