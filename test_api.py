from __future__ import annotations

from pathlib import Path

import pytest
from biliass import convert_to_ass

CORPUS_DIR = Path(__file__).parent / "corpus"


@pytest.mark.biliass
def test_protobuf():
    cid = 18678311
    protobuf_paths = CORPUS_DIR.joinpath("protobuf").glob(f"{cid}-*.pb")
    protobuf_bytes: list[bytes] = []
    for path in protobuf_paths:
        with path.open("rb") as f:
            protobuf_bytes.append(f.read())
    convert_to_ass(protobuf_bytes, 1920, 1080, input_format="protobuf")


@pytest.mark.biliass
def test_xml_v1_text():
    cid = 18678311
    xml_path = CORPUS_DIR.joinpath(f"xml/{cid}.xml")
    with xml_path.open("r") as f:
        convert_to_ass(f.read(), 1920, 1080)


@pytest.mark.biliass
def test_xml_v1_bytes():
    cid = 18678311
    xml_path = CORPUS_DIR.joinpath(f"xml/{cid}.xml")
    with xml_path.open("rb") as f:
        convert_to_ass(f.read(), 1920, 1080)
