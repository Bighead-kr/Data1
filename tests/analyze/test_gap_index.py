import pandas as pd
from src.analyze.gap_index import compute_gap_index

def test_compute_gap_index_ranks_lower_supply_as_more_scarce():
    facilities_df = pd.DataFrame(
        {"region_code": ["A", "A", "B"], "capacity": [50, 50, 200]}
    )
    population_df = pd.DataFrame(
        {"region_code": ["A", "B"], "elderly_population": [10000, 10000]}
    )

    result = compute_gap_index(facilities_df, population_df)

    row_a = result[result["region_code"] == "A"].iloc[0]
    row_b = result[result["region_code"] == "B"].iloc[0]

    assert row_a["total_capacity"] == 100
    assert row_a["capacity_per_1000_elderly"] == 10.0
    assert row_b["capacity_per_1000_elderly"] == 20.0
    assert row_a["gap_rank"] == 1
    assert row_b["gap_rank"] == 2

def test_compute_gap_index_handles_region_with_zero_facilities():
    facilities_df = pd.DataFrame({"region_code": ["A"], "capacity": [50]})
    population_df = pd.DataFrame(
        {"region_code": ["A", "B"], "elderly_population": [10000, 5000]}
    )

    result = compute_gap_index(facilities_df, population_df)
    row_b = result[result["region_code"] == "B"].iloc[0]

    assert row_b["total_capacity"] == 0
    assert row_b["capacity_per_1000_elderly"] == 0.0
