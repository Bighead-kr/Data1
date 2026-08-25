import os

import pandas as pd

from src.clean.region_mapper import build_region_lookup
from src.clean.clean_facilities import clean_facilities
from src.clean.clean_population import clean_population
from src.analyze.gap_index import compute_gap_index


def run_pipeline(raw_dir: str, processed_dir: str) -> str:
    region_lookup = build_region_lookup(os.path.join(raw_dir, "region_codes_raw.csv"))
    general = pd.read_csv(os.path.join(raw_dir, "ltc_facilities_general.csv"), dtype=str)
    capacity = pd.read_csv(os.path.join(raw_dir, "ltc_facilities_capacity.csv"), dtype=str)
    pop_raw = pd.read_csv(
        os.path.join(raw_dir, "인구총조사_고령인구비율_시도_시_군_구__20260825134933.csv"),
        dtype=str,
    )

    facilities_df = clean_facilities(general, capacity, region_lookup)
    population_df = clean_population(pop_raw, region_lookup)

    result = compute_gap_index(facilities_df, population_df)

    output_path = os.path.join(processed_dir, "gap_index.csv")
    result.to_csv(output_path, index=False)
    return output_path
