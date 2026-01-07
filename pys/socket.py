import asyncio
import datetime
import json
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import tornado.web
import tornado.websocket
import tornado.ioloop
from pys.functions import check_client_limit, get_resolver_from_db, single_query, insert_result_to_db

clients = {}
POOL = ThreadPoolExecutor(max_workers=20)

class WSHandler(tornado.websocket.WebSocketHandler):

    def check_origin(self, origin):
        return True

    async def run_dns_check(self, query_name, query_type):

        servers = get_resolver_from_db()

        loop = asyncio.get_running_loop()

        all_result = []

        tasks = [
            loop.run_in_executor(POOL, single_query, s, query_name, query_type)
            for s in servers
        ]

        for coro in asyncio.as_completed(tasks):
            result = await coro
            all_result.append(result)

            await self.write_message(json.dumps({"type": "resolver_result","data": result}, ensure_ascii=False, default=str))

        doc = {"dns_results": all_result,"client_id": self.client_id,"client_ip_address": self.client_ip_address,"created_at": datetime.now(timezone.utc),}

        return doc

    def open(self):

        self.client_id = str(uuid.uuid4())
        clients[self.client_id] = self

        xff = self.request.headers.get("X-Forwarded-For")
        if xff:
            self.client_ip_address = xff.split(",")[0].strip()
        else:
            self.client_ip_address = self.request.headers.get("X-Real-IP", self.request.remote_ip)

        self.write_message(json.dumps({"client_id": self.client_id, "client_ip_address":self.client_ip_address, "type":"message", "text":"connection successful"}))

    async def on_message(self, message):


        data = json.loads(message)
        client_id = self.client_id
        query_name = data.get("query_name")
        query_type = data.get("query_type")


        if not query_name or not query_type:
            if client_id in clients:
                await self.write(json.dumps({"client_id": self.client_id, "type":"message", "text":"Query Name or Type Can Not Be Empty."}))

        check_limit = check_client_limit(self.client_ip_address)

        if not check_limit:
            await self.write_message(json.dumps({"client_id": self.client_id, "type": "message", "text": "You Have No Limit"}))
            return

        if not client_id or client_id not in clients:
            await self.write_message(json.dumps({"type": "message","message": "Client Not Found"}))
            return


        doc = await self.run_dns_check(query_name,query_type)

        insert_result_to_db(doc)

        await self.write_message(json.dumps({"client_id": self.client_id, "type": "message", "text": "done"}))

    def on_close(self):
        if hasattr(self, 'uid') and self.uid in clients:
            del clients[self.uid]


app = tornado.web.Application([(r"/", WSHandler),])

if __name__ == "__main__":
    print("🚀 Socket Started by Ali on 3654 🚀")
    app.listen(3654, address="0.0.0.0")
    tornado.ioloop.IOLoop.current().start()

