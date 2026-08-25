import json

import pandas as pd

from src.clean.region_mapper import combine_region_key

# 좌표 원본(gist 데이터)이 도(道) 명칭 개편 이전 데이터라 발생하는 불일치.
SIDO_NAME_ALIASES = {
    "강원특별자치도": "강원도",
    "전북특별자치도": "전라북도",
}

# 관할 구역이 이후에 변경/개칭된 시군구 (미추홀구는 남구의 개칭, 군위군은
# 2023년 경북->대구 편입) — 좌표 원본은 옛 소속·이름 기준이라 예외 매핑.
SIGUNGU_ALIASES = {
    ("인천광역시", "미추홀구"): ("인천광역시", "남구"),
    ("대구광역시", "군위군"): ("경상북도", "군위군"),
}

# 좌표 원본에 항목 자체가 없는 지역 (세종시는 시군구 구분이 없어 통째로 누락됨).
MANUAL_COORDS = {
    "세종특별자치시세종특별자치시": (36.4800, 127.2890),
}


def load_centroid_coords(coords_json_path: str) -> dict[str, tuple[float, float]]:
    with open(coords_json_path, encoding="utf-8") as f:
        raw = json.load(f)
    lookup = {}
    for key, value in raw.items():
        sido, sigungu = key.split("/")
        lookup[combine_region_key(sido, sigungu)] = (float(value["lat"]), float(value["long"]))
    return lookup


def build_region_coords(coords_json_path: str, region_codes_path: str) -> dict[str, tuple[float, float]]:
    coord_lookup = load_centroid_coords(coords_json_path)

    df = pd.read_csv(region_codes_path, dtype=str)
    df["code_len"] = df["code"].str.len()
    sido_names = dict(zip(df.loc[df["code_len"] == 2, "code"], df.loc[df["code_len"] == 2, "name"]))

    result = {}
    for _, row in df.loc[df["code_len"] == 5].iterrows():
        sido_name = sido_names.get(row["code"][:2])
        if sido_name is None:
            continue
        sigungu_name = row["name"]

        alias_sido, alias_sigungu = SIGUNGU_ALIASES.get(
            (sido_name, sigungu_name), (sido_name, sigungu_name)
        )
        alias_sido = SIDO_NAME_ALIASES.get(alias_sido, alias_sido)
        alias_key = combine_region_key(alias_sido, alias_sigungu)

        if alias_key in coord_lookup:
            result[row["code"]] = coord_lookup[alias_key]
            continue

        manual_key = combine_region_key(sido_name, sigungu_name)
        if manual_key in MANUAL_COORDS:
            result[row["code"]] = MANUAL_COORDS[manual_key]

    return result
