import datetime
import time
from datetime import datetime, timezone, timedelta

import dns.resolver

from pys.config import CLIENT_DAY_LIMIT, CLIENT_HOUR_LIMIT, CLIENT_MINUTE_LIMIT, RESOLVER_TIMEOUT, RESOLVER_LIFETIME
from pys.db import get_db


def get_resolver_from_db():
    db = get_db()
    docs = list(db.resolvers.find({}))
    return docs


def check_client_limit(client_ip_address: str):
    db = get_db()

    now = datetime.now(timezone.utc)

    one_day_ago = now - timedelta(days=1)
    one_hour_ago = now - timedelta(minutes=60)
    one_min_ago = now - timedelta(minutes=1)

    day_count = db.results.count_documents({
        "client_ip_address": client_ip_address,
        "created_at": {"$gte": one_day_ago}
    })

    hour_count = db.results.count_documents({
        "client_ip_address": client_ip_address,
        "created_at": {"$gte": one_hour_ago}
    })

    minute_count = db.results.count_documents({
        "client_ip_address": client_ip_address,
        "created_at": {"$gte": one_min_ago}
    })

    if int(day_count) >= int(CLIENT_DAY_LIMIT):
        return False, "day_limit"
    if int(hour_count) >= int(CLIENT_HOUR_LIMIT):
        return False, "hour_limit"
    if int(minute_count) >= int(CLIENT_MINUTE_LIMIT):
        return False, "minute_limit"
    else:
        return True, None


def insert_result_to_db(data: dict):
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
    resolver.timeout = RESOLVER_TIMEOUT
    resolver.lifetime = RESOLVER_LIFETIME
    start = time.perf_counter()

    try:
        answers = resolver.resolve(query_name, query_type)

        latency_ms = (time.perf_counter() - start) * 1000
        ttl = answers.rrset.ttl if answers.rrset else None

        results = [a.to_text() for a in answers]

        result_text = ", ".join(results) if results else ""

        return {
            "country": country,
            "name": name,
            "server_ip": server_ip,
            "flag": flag,
            "latency_ms": round(latency_ms, 2),
            "ttl": ttl,
            "status": True,
            "result": result_text,
            "results": results,
            "result_count": len(results),
        }




    except Exception as e:
        latency_ms = (time.perf_counter() - start) * 1000
        err = str(e)

        data = {
            "country": country,
            "name": name,
            "server_ip": server_ip,
            "flag": flag,
            "latency_ms": round(latency_ms, 2),
            "ttl": None,
            "status": False,
            "result": err,
            "results": [err],
            "result_count": 0,
        }

    return data
