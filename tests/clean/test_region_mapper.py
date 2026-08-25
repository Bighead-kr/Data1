import pandas as pd
from src.clean.region_mapper import (
    normalize_region_name,
    combine_region_key,
    build_region_lookup,
    build_region_name_lookup,
)

def test_normalize_region_name_strips_whitespace_and_parens():
    assert normalize_region_name(" 장안구 (경기) ") == "장안구"

def test_combine_region_key_joins_normalized_parts():
    assert combine_region_key("경기도", " 수원시 장안구 ") == "경기도수원시장안구"

def test_build_region_lookup_uses_parent_sido_code_prefix(tmp_path):
    csv_path = tmp_path / "region_codes_raw.csv"
    pd.DataFrame(
        {
            "code": ["11", "11010", "11020", "41", "41111"],
            "name": ["서울특별시", "종로구", "중구", "경기도", "수원시장안구"],
        }
    ).to_csv(csv_path, index=False)

    lookup = build_region_lookup(str(csv_path))

    assert lookup["서울특별시종로구"] == "11010"
    assert lookup["서울특별시중구"] == "11020"
    assert lookup["경기도수원시장안구"] == "41111"


def test_build_region_name_lookup_maps_code_to_sido_sigungu_display_name(tmp_path):
    csv_path = tmp_path / "region_codes_raw.csv"
    pd.DataFrame(
        {
            "code": ["11", "11010", "41", "41111"],
            "name": ["서울특별시", "종로구", "경기도", "수원시장안구"],
        }
    ).to_csv(csv_path, index=False)

    names = build_region_name_lookup(str(csv_path))

    assert names["11010"] == "서울특별시 종로구"
    assert names["41111"] == "경기도 수원시장안구"
