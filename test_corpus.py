from __future__ import annotations

import hashlib
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from biliass import convert_to_ass

if TYPE_CHECKING:
    from syrupy.assertion import SnapshotAssertion


CORPUS_DIR = Path(__file__).parent / "corpus"
CORPUS_XML_CIDS = [(path.stem,) for path in CORPUS_DIR.glob("xml/*.xml")]
CORPUS_PB_CIDS = list({(path.stem.split("-")[0],) for path in CORPUS_DIR.glob("protobuf/*.pb")})


def sha256_str(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def sha256_bytes(text: bytes) -> str:
    return hashlib.sha256(text).hexdigest()


def load_xml_danmaku(cid: str) -> str:
    with Path(CORPUS_DIR / f"xml/{cid}.xml").open("r") as f:
        return f.read()


def load_protobuf_danmaku(cid: str) -> list[bytes]:
    res: list[bytes] = []
    paths = sorted(Path(CORPUS_DIR / "protobuf").glob(f"{cid}-*.pb"), key=lambda path: path.stem)
    for path in paths:
        with path.open("rb") as f:
            res.append(f.read())
    return res


@pytest.mark.benchmark
@pytest.mark.biliass
@pytest.mark.parametrize(
    ("cid",),
    CORPUS_XML_CIDS,
)
def test_xml_corpus(snapshot: SnapshotAssertion, cid: str):
    source_danmaku = load_xml_danmaku(cid)
    assert sha256_str(source_danmaku) == snapshot(name="source_hash")
    ass_danmaku = convert_to_ass(source_danmaku, 1920, 1080, reduce_comments=False)
    assert ass_danmaku == snapshot(name="ass")


@pytest.mark.benchmark
@pytest.mark.biliass
@pytest.mark.parametrize(
    ("cid",),
    CORPUS_PB_CIDS,
)
def test_protobuf_corpus(snapshot: SnapshotAssertion, cid: str):
    source_danmakus = load_protobuf_danmaku(cid)
    source_hash = ", ".join([sha256_bytes(source_danmaku) for source_danmaku in source_danmakus])
    assert source_hash == snapshot(name="source_hash")
    ass_danmaku = convert_to_ass(source_danmakus, 1920, 1080, input_format="protobuf", reduce_comments=False)
    assert ass_danmaku == snapshot(name="ass")
