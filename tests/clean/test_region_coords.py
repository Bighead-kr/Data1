import json

import pandas as pd

from src.clean.region_coords import build_region_coords


def _write_region_codes(path):
    pd.DataFrame(
        {
            "code": ["11", "11010", "42", "42110", "29", "29010"],
            "name": ["서울특별시", "종로구", "강원특별자치도", "춘천시", "세종특별자치시", "세종특별자치시"],
        }
    ).to_csv(path, index=False)


def _write_coords(path):
    # 좌표 원본은 도(道) 개편 이전 이름(강원도)을 쓰고, 세종은 아예 항목이 없는
    # 실제 gist 데이터의 특성을 그대로 재현한 fixture.
    data = {
        "서울특별시/종로구": {"lat": "37.5", "long": "126.9"},
        "강원도/춘천시": {"lat": "37.8", "long": "127.7"},
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)


def test_build_region_coords_resolves_renamed_sido_via_alias(tmp_path):
    region_codes_path = tmp_path / "region_codes_raw.csv"
    coords_path = tmp_path / "coords.json"
    _write_region_codes(region_codes_path)
    _write_coords(coords_path)

    coords = build_region_coords(str(coords_path), str(region_codes_path))

    assert coords["11010"] == (37.5, 126.9)
    assert coords["42110"] == (37.8, 127.7)  # 강원특별자치도 -> 강원도 alias로 매칭


def test_build_region_coords_falls_back_to_manual_coords_for_sejong(tmp_path):
    region_codes_path = tmp_path / "region_codes_raw.csv"
    coords_path = tmp_path / "coords.json"
    _write_region_codes(region_codes_path)
    _write_coords(coords_path)  # 좌표 원본에 세종 항목 없음

    coords = build_region_coords(str(coords_path), str(region_codes_path))

    assert coords["29010"] == (36.4800, 127.2890)
