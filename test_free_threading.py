from __future__ import annotations

import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from biliass import convert_to_ass

CORPUS_DIR = Path(__file__).parent / "corpus"


def read_bytes_from_path(path: Path):
    with path.open("rb") as f:
        return f.read()


@pytest.mark.biliass
def test_free_threading():
    cid = "371495955"
    protobuf_paths = (CORPUS_DIR / "protobuf").glob(f"{cid}-*.pb")
    protobuf_bytes = [read_bytes_from_path(path) for path in protobuf_paths]

    n_threads = 24
    barrier = threading.Barrier(n_threads)

    def closure():
        # Ensure that all threads reach this point before concurrent execution.
        barrier.wait()
        r = convert_to_ass(protobuf_bytes, 1920, 1080, input_format="protobuf")
        return r

    with ThreadPoolExecutor(max_workers=n_threads) as executor:
        futures = [executor.submit(closure) for _ in range(n_threads)]

    results = [f.result() for f in futures]
    for result in results[1:]:
        assert result == results[0]
