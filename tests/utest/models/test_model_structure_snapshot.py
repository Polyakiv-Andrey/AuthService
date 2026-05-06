import pytest

from src.models import Base

all_tables = list(Base.metadata.tables.values())


@pytest.mark.parametrize("table", all_tables, ids=lambda t: t.name)
def test_model_structure_snapshot(table, snapshot):
    columns_data = {}
    for column in table.columns:
        columns_data[column.name] = {
            "type": str(column.type),
            "nullable": column.nullable,
            "default": str(column.server_default.arg) if column.server_default else None,
        }

    indices_data = {}
    for idx in table.indexes:
        indices_data[idx.name] = {
            "columns": [col.name for col in idx.columns],
            "unique": idx.unique,
        }
    current_structure = {
        "table_name": table.name,
        "columns": columns_data,
        "indices": indices_data,
        "primary_key": [col.name for col in table.primary_key],
    }
    snapshot.snapshot_dir = "tests/utest/models/snapshots"
    snapshot.assert_match(str(current_structure), f"{table.name}_snapshot.json")
