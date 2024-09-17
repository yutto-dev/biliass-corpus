from __future__ import annotations

import asyncio
from pathlib import Path

import aiofiles
import httpx

CORPUS_CIDS = [
    "18678311",
    "2170097",  # av1440943
    "285968687",  # BV1cf4y1C7mo
    "371495955",  # BV1aW41187Qw?p=2
    "527533",  # BV14x411F71o?p=1
    "527534",  # BV14x411F71o?p=2
    "527535",  # BV14x411F71o?p=3
    "527536",  # BV14x411F71o?p=4
    "2428566",  # BV14x411F71o?p=5
    "16433563",  # BV16x411D7NK
    "745913430",  # ep84340
    "1176840",  # BV1Js411o76u
]
CORPUS_DIR = Path("corpus")

BILIBILI_HEADERS: dict[str, str] = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Referer": "https://www.bilibili.com",
}


async def download_xml_danmaku(client: httpx.AsyncClient, cid: str, corpus_dir: Path):
    corpus_dir.mkdir(parents=True, exist_ok=True)
    resp = await client.get(
        f"http://comment.bilibili.com/{cid}.xml",
        headers=BILIBILI_HEADERS,
        follow_redirects=True,
    )
    resp.encoding = "utf-8"
    async with aiofiles.open(corpus_dir.joinpath(f"{cid}.xml"), "w") as f:
        await f.write(resp.text)


async def main():
    async with httpx.AsyncClient() as client:
        await asyncio.gather(*[download_xml_danmaku(client, cid, CORPUS_DIR / "xml") for cid in CORPUS_CIDS])


if __name__ == "__main__":
    asyncio.run(main())
