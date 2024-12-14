from __future__ import annotations

import argparse
import asyncio
from pathlib import Path
from urllib.parse import quote, unquote

import aiofiles
import httpx

from yutto._typing import AId, AvId, BvId, CId
from yutto.api.danmaku import get_protobuf_danmaku, get_xml_danmaku
from yutto.utils.fetcher import FetcherContext, create_client

CORPUS_IDS: list[tuple[AvId, CId]] = [
    (BvId("BV1vx41187Jd"), CId("18678311")),  # BV1vx41187Jd
    (AId("1440943"), CId("2170097")),  # av1440943
    (BvId("BV1cf4y1C7mo"), CId("285968687")),  # BV1cf4y1C7mo
    (BvId("BV1aW41187Qw"), CId("371495955")),  # BV1aW41187Qw?p=2
    (BvId("BV14x411F71o"), CId("527533")),  # BV14x411F71o?p=1
    (BvId("BV14x411F71o"), CId("527534")),  # BV14x411F71o?p=2
    (BvId("BV14x411F71o"), CId("527535")),  # BV14x411F71o?p=3
    (BvId("BV14x411F71o"), CId("527536")),  # BV14x411F71o?p=4
    (BvId("BV14x411F71o"), CId("2428566")),  # BV14x411F71o?p=5
    (BvId("BV16x411D7NK"), CId("16433563")),  # BV16x411D7NK
    (AId("3934631"), CId("745913430")),  # ep84340
    (BvId("BV1Js411o76u"), CId("1176840")),  # BV1Js411o76u
    (BvId("BV114421Q7yh"), CId("1600157973")),  # BV114421Q7yh
    (BvId("BV1dS411c7sm"), CId("1617171254")),  # BV1dS411c7sm
    (BvId("BV19U411m7PK"), CId("1660054944")),  # BV19U411m7PK
]
CORPUS_DIR = Path("corpus")

BILIBILI_HEADERS: dict[str, str] = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Referer": "https://www.bilibili.com",
}


def cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download Bilibili danmaku corpus")
    parser.add_argument("-w", "--overwrite", action="store_true", help="Overwrite existing corpus")
    parser.add_argument("-c", "--sessdata", default="", help="Cookies 中的 SESSDATA 字段")
    return parser.parse_args()


async def download_xml_danmaku(
    ctx: FetcherContext, client: httpx.AsyncClient, cid: CId, corpus_dir: Path, overwrite: bool = False
):
    corpus_dir.mkdir(parents=True, exist_ok=True)
    corpus_file_path = corpus_dir.joinpath(f"{cid}.xml")
    if not overwrite and corpus_file_path.exists():
        return
    xml_text = await get_xml_danmaku(ctx, client, cid)
    async with aiofiles.open(corpus_file_path, "w") as f:
        await f.write(xml_text)


async def download_protobuf_danmaku(
    ctx: FetcherContext, client: httpx.AsyncClient, avid: AvId, cid: CId, corpus_dir: Path, overwrite: bool = False
):
    corpus_dir.mkdir(parents=True, exist_ok=True)
    corpus_first_file_path = corpus_dir.joinpath(f"{cid}-0.pb")
    if not overwrite and corpus_first_file_path.exists():
        return
    protobuf_bytes_list = await get_protobuf_danmaku(ctx, client, avid, cid)
    for i, protobuf_bytes in enumerate(protobuf_bytes_list):
        corpus_file_path = corpus_dir.joinpath(f"{cid}-{i}.pb")
        async with aiofiles.open(corpus_file_path, "wb") as f:
            await f.write(protobuf_bytes)


async def main():
    args = cli()
    cookies = httpx.Cookies()
    cookies.set("SESSDATA", quote(unquote(args.sessdata)))
    ctx = FetcherContext()
    async with create_client(
        cookies=cookies,
    ) as client:
        await asyncio.gather(
            *[download_xml_danmaku(ctx, client, cid, CORPUS_DIR / "xml", args.overwrite) for _, cid in CORPUS_IDS]
        )
        await asyncio.gather(
            *[
                download_protobuf_danmaku(ctx, client, avid, cid, CORPUS_DIR / "protobuf", args.overwrite)
                for avid, cid in CORPUS_IDS
            ]
        )


if __name__ == "__main__":
    asyncio.run(main())
