import pandas as pd
import pytest
from src.collect.load_raw import load_and_validate


def test_load_and_validate_returns_dataframe_when_columns_present(tmp_path):
    csv_path = tmp_path / "sample.csv"
    pd.DataFrame({"a": [1], "b": [2]}).to_csv(csv_path, index=False)

    result = load_and_validate(str(csv_path), required_columns=["a", "b"])

    assert list(result.columns) == ["a", "b"]
    assert len(result) == 1


def test_load_and_validate_raises_when_required_column_missing(tmp_path):
    csv_path = tmp_path / "sample.csv"
    pd.DataFrame({"a": [1]}).to_csv(csv_path, index=False)

    with pytest.raises(ValueError, match="missing required columns"):
        load_and_validate(str(csv_path), required_columns=["a", "b"])
