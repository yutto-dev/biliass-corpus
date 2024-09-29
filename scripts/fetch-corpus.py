from __future__ import annotations

import argparse
import asyncio
from pathlib import Path
from urllib.parse import quote, unquote

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
    "1600157973",  # BV114421Q7yh
    "1617171254",  # BV1dS411c7sm
    "1660054944",  # BV19U411m7PK
]
CORPUS_DIR = Path("corpus")

BILIBILI_HEADERS: dict[str, str] = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Referer": "https://www.bilibili.com",
}


def cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download Bilibili danmaku corpus")
    parser.add_argument("-w", "--overwrite", action="store_true", help="Overwrite existing corpus")
    parser.add_argument("-c", "--sessdata", default="", help="Cookies 中的 SESSDATA 字段")
    return parser.parse_args()


async def download_xml_danmaku(client: httpx.AsyncClient, cid: str, corpus_dir: Path, overwrite: bool = False):
    corpus_dir.mkdir(parents=True, exist_ok=True)
    corpus_file_path = corpus_dir.joinpath(f"{cid}.xml")
    if not overwrite and corpus_file_path.exists():
        return
    resp = await client.get(
        f"http://comment.bilibili.com/{cid}.xml",
        follow_redirects=True,
    )
    resp.encoding = "utf-8"
    async with aiofiles.open(corpus_file_path, "w") as f:
        await f.write(resp.text)


async def download_protobuf_danmaku(client: httpx.AsyncClient, cid: str, corpus_dir: Path, overwrite: bool = False):
    corpus_dir.mkdir(parents=True, exist_ok=True)
    corpus_file_path = corpus_dir.joinpath(f"{cid}.pb")
    if not overwrite and corpus_file_path.exists():
        return
    resp = await client.get(
        f"http://api.bilibili.com/x/v2/dm/web/seg.so?type=1&oid={cid}&segment_index={1}",
    )
    async with aiofiles.open(corpus_file_path, "wb") as f:
        await f.write(resp.content)


async def main():
    args = cli()
    cookies = httpx.Cookies()
    cookies.set("SESSDATA", quote(unquote(args.sessdata)))
    async with httpx.AsyncClient(
        headers=BILIBILI_HEADERS,
        cookies=cookies,
    ) as client:
        await asyncio.gather(
            *[download_xml_danmaku(client, cid, CORPUS_DIR / "xml", args.overwrite) for cid in CORPUS_CIDS]
        )
        await asyncio.gather(
            *[download_protobuf_danmaku(client, cid, CORPUS_DIR / "protobuf", args.overwrite) for cid in CORPUS_CIDS]
        )


if __name__ == "__main__":
    asyncio.run(main())
