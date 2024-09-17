from __future__ import annotations

import hashlib
import random
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from biliass import Danmaku2ASS

if TYPE_CHECKING:
    from syrupy.assertion import SnapshotAssertion

CORPUS_DIR = Path(__file__).parent / "corpus"
CORPUS_XML_CIDS = [(path.stem,) for path in CORPUS_DIR.glob("xml/*.xml")]


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def load_danmaku(cid: str) -> str:
    with Path(CORPUS_DIR / f"xml/{cid}.xml").open("r") as f:
        return f.read()


@pytest.mark.biliass
@pytest.mark.parametrize(
    ("cid",),
    CORPUS_XML_CIDS,
)
def test_corpus(snapshot: SnapshotAssertion, cid: str):
    random.seed(1127)
    source_danmaku = load_danmaku(cid)
    assert sha256(source_danmaku) == snapshot(name="source_hash")
    ass_danmaku = Danmaku2ASS(source_danmaku, 1920, 1080)
    assert ass_danmaku == snapshot(name="ass")
