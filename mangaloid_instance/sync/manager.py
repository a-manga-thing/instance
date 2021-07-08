from asyncio import Queue, get_event_loop, Lock
from .utils import create_sync_payload
from enum import Enum
from aiohttp import ClientSession
from logging import getLogger

class SyncEvents(Enum):
    CREATE = 1
    MODIFY = 2
    DELETE = 3

class SyncItem:
    def __init__(self, payload, event):
        self.payload = payload.to_dict()
        self.event_type = event
        self.item_type = payload.__name__

    async def get_body(self, instance, self_address):
        payload = await create_sync_payload(self.payload, instance.public_key)
        return {
            "action" : self.event_type.name,
            "item_type" : self.item_types,
            "instance" : self_address,
            "payload" : payload
        }

class Approval:
    def __init__(self, payload):
        self.id = str(hash(frozenset(payload.items())))
        self.payload = payload
        self.lock = Lock()
        self.approved = False

    async def wait_for_approval(self, manager):
        await self.lock.acquire()
        if self.approved:
            if self.payload["action"] == "CREATE":
                pass
            elif self.payload["action"] == "MODIFY":
                pass
            elif self.payload["action"] == "DELETE":
                pass

    def approve(self):
        self.approved = True
        self.lock.release()

    def reject(self):
        self.lock.release()

class SyncManager:
    def __init__(self, ctx):
        self.instance = ctx
        self.db = ctx.db
        self.address = ctx.config.instance_address
        self.queue = Queue()
        self.approvals = {}
        self.http = ClientSession()
        self.logger = getLogger("sync-manager")

    def add_approval(self, payload):
        ap = Approval(payload)
        self.approvals[ap.id] = ap
        get_event_loop().create_task(self.approvals[ap.id].wait_for_approval(self))

    def add(self, obj):
        self.queue.put_nowait(SyncItem(obj, SyncEvents.CREATE))

    def update(self, obj):
        self.queue.put_nowait(SyncItem(obj, SyncEvents.MODIFY))

    def remove(self, obj):
        self.queue.put_nowait(SyncItem(obj, SyncEvents.DELETE))

    async def start(self):
        self.logger.info("Starting sync manager loop")
        while True:
            item = await self.queue.get()
            instances = await self.db.select_all_instances()
            for instance in instances:
                try:
                    body = item.get_body(instance, self.address)
                    r = await self.http.post(instance.address, json=body)
                    if r.status == 403:
                        pass #TODO: Remove this instance
                except Exception as e:
                    self.logger.warn("Failed to send sync to {} ({})".format(instance.address, e))