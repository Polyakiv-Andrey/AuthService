import inspect

import src.models as models
from src.models import Base


def test_base_model_fields():
    class MockModel(Base):
        pass

    columns = MockModel.__table__.columns
    assert len(columns) == 3

    id_column = columns["id"]
    assert id_column.primary_key is True
    assert str(id_column.server_default.arg) == "gen_random_uuid()"

    created_col = columns["created_at"]
    assert created_col.type.timezone is True
    assert "now" in str(created_col.server_default.arg).lower()

    updated_col = columns["updated_at"]
    assert updated_col.onupdate is not None


def test_base_tablename():
    class Test(Base):
        pass

    assert Test.__tablename__ == "test"


def test_all_models_extend_base_model():
    for name in models.__all__:
        model_class = getattr(models, name)
        if inspect.isclass(model_class):
            if model_class is not Base:
                assert issubclass(model_class, Base)
