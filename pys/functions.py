import asyncio
import datetime
import time
import dns.resolver
from datetime import datetime, timezone, timedelta
from pys.config import CLIENT_LIMIT
from pys.db import get_db





def get_resolver_from_db():
    db = get_db()
    docs = list(db.resolvers.find({}))
    return docs

def check_client_limit(client_ip_address:str):

    db = get_db()

    now = datetime.now(timezone.utc)

    one_min_ago = now - timedelta(minutes=1)

    count = db.results.count_documents({
        "client_ip_address": client_ip_address,
        "created_at": {"$gte": one_min_ago}
    })


    limit = CLIENT_LIMIT

    if int(count) >= int(limit):
        return False
    else:
        return True

def insert_result_to_db(data:dict):

    db = get_db()

    db.results.insert_one(data)

    return True


def single_query(server: dict, query_name: str, query_type: str):
    country = server['country']
    name = server['name']
    server_ip = server['dns']
    flag = server['flag']

    resolver = dns.resolver.Resolver(configure=False)
    resolver.nameservers = [server_ip]
    resolver.timeout = 1.5
    resolver.lifetime = 3

    data = {}
    start = time.perf_counter()

    try:
        answers = resolver.resolve(query_name, query_type)

        for answer in answers:
            latency_ms = (time.perf_counter() - start) * 1000
            ttl = answers.rrset.ttl if answers.rrset else None
            data = {
                "country": country,
                "name": name,
                "server_ip": server_ip,
                "flag": flag,
                "latency_ms": round(latency_ms, 2),
                "ttl": ttl,
                "status": True,
                "result": answer.to_text(),
            }


    except Exception as e:
        latency_ms = (time.perf_counter() - start) * 1000
        data = {
            "country": country,
            "name": name,
            "server_ip": server_ip,
            "flag": flag,
            "latency_ms": round(latency_ms, 2),
            "ttl": None,
            "status": False,
            "result": str(e),
        }
    return data




