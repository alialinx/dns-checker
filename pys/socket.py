



class DNSWebSocketHandler:
    def __init__(self, websocket):
        self.ws = websocket

    async def open(self):
        pass

    async def message(self, msg: str):
        pass

    async def close(self):
        pass

    async def run(self):
        await self.open()
        try:
            async for msg in self.ws:
                await self.message(msg)
        finally:
            await self.close()
