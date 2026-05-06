from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def set_snapshot_path(snapshot):
    snapshot.snapshot_dir = Path(__file__).parent / "snapshots"
