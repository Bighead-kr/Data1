import os

import pandas as pd

from src.clean.region_mapper import build_region_lookup, build_region_name_lookup
from src.clean.region_coords import build_region_coords
from src.clean.clean_facilities import clean_facilities
from src.clean.clean_population import clean_population
from src.analyze.gap_index import compute_gap_index


def run_pipeline(raw_dir: str, processed_dir: str) -> str:
    region_codes_path = os.path.join(raw_dir, "region_codes_raw.csv")
    region_lookup = build_region_lookup(region_codes_path)
    region_names = build_region_name_lookup(region_codes_path)
    region_coords = build_region_coords(
        os.path.join(raw_dir, "sigungu_centroid_coords_raw.json"), region_codes_path
    )
    general = pd.read_csv(os.path.join(raw_dir, "ltc_facilities_general.csv"), dtype=str)
    capacity = pd.read_csv(os.path.join(raw_dir, "ltc_facilities_capacity.csv"), dtype=str)
    pop_raw = pd.read_csv(
        os.path.join(raw_dir, "인구총조사_고령인구비율_시도_시_군_구__20260825134933.csv"),
        dtype=str,
    )

    facilities_df = clean_facilities(general, capacity, region_lookup)
    population_df = clean_population(pop_raw, region_lookup)

    result = compute_gap_index(facilities_df, population_df)
    # Tableau 지도/툴팁에서 코드 대신 지역명을 바로 보여주기 위해 붙인다.
    result.insert(1, "region_name", result["region_code"].map(region_names))
    # Tableau 심볼 지도(위도/경도 기반)를 위한 시군구 중심좌표.
    result["lat"] = result["region_code"].map(lambda c: region_coords.get(c, (None, None))[0])
    result["lon"] = result["region_code"].map(lambda c: region_coords.get(c, (None, None))[1])

    output_path = os.path.join(processed_dir, "gap_index.csv")
    result.to_csv(output_path, index=False)
    return output_path
