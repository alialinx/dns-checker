import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import dns.resolver

from pys.db import get_db


def get_resolver_from_db():
    db = get_db()
    docs = list(db.resolvers.find({}))
    return docs


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
            "result": e,
        }
    return data


def check_dns(query_name:str, query_type:str):

    dns_servers = get_resolver_from_db()


    with ThreadPoolExecutor(max_workers=20) as pool:

        results = []

        futures = [pool.submit(single_query, s, query_name, query_type) for s in dns_servers]

        for future in as_completed(futures):
            results.append(future.result())

    print(results)
    return results


