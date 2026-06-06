import ipaddress
import os
from typing import Any, Iterable

import requests

WETEST_CF2DNS_KEY = os.getenv("WETEST_CF2DNS_KEY")

SOURCES = [
    (
        "cloudflare",
        "https://www.wetest.vip/api/cf2dns/get_cloudflare_ip",
        WETEST_CF2DNS_KEY,
    ),
    (
        "cloudfront",
        "https://www.wetest.vip/api/cf2dns/get_cloudfront_ip",
        WETEST_CF2DNS_KEY,
    ),
]


def is_ipv4(value: str) -> bool:
    try:
        return ipaddress.ip_address(value).version == 4
    except Exception:
        return False


def walk_values(obj: Any) -> Iterable[str]:
    if isinstance(obj, dict):
        for value in obj.values():
            yield from walk_values(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from walk_values(item)
    elif isinstance(obj, str):
        yield obj


def extract_ips(payload: Any) -> list[str]:
    ips: list[str] = []
    seen: set[str] = set()

    for value in walk_values(payload):
        if is_ipv4(value) and value not in seen:
            seen.add(value)
            ips.append(value)

    return ips


def fetch_source(name: str, url: str, key: str) -> list[str]:
    if not key:
        print(f"[skip] {name}: missing env key")
        return []

    print(f"[get] {name}: {url}")
    response = requests.get(
        url,
        params={"key": key, "type": "v4"},
        headers={"User-Agent": "cf-best-domain/1.0"},
        timeout=20,
    )
    response.raise_for_status()

    data = response.json()
    ips = extract_ips(data)

    print(f"[ok] {name}: {len(ips)} IPs")
    return ips


def main() -> None:
    all_ips: list[str] = []
    seen: set[str] = set()

    for name, url, key in SOURCES:
        for ip in fetch_source(name, url, key):
            if ip not in seen:
                seen.add(ip)
                all_ips.append(ip)

    with open("ip.txt", "w", encoding="utf-8") as f:
        for ip in all_ips:
            f.write(f"{ip}\n")

    print(f"saved {len(all_ips)} unique IPv4 addresses to ip.txt")


if __name__ == "__main__":
    main()
