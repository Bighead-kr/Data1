import pandas as pd
from src.clean.clean_population import clean_population

def test_clean_population_drops_summary_rows_and_maps_region_code():
    raw_df = pd.DataFrame(
        {
            "행정구역별(1)": ["행정구역별(1)", "전국", "서울특별시", "서울특별시", "세종특별자치시"],
            "행정구역별(2)": ["행정구역별(2)", "소계", "소계", "종로구", "소계"],
            "2025.1": ["65세이상인구 (명)", "10722557", "1881288", "29432", "50000"],
        }
    )
    region_lookup = {"서울특별시종로구": "11010", "세종특별자치시세종특별자치시": "36110"}

    result = clean_population(raw_df, region_lookup)

    assert set(result["region_code"]) == {"11010", "36110"}
    row = result[result["region_code"] == "11010"].iloc[0]
    assert row["elderly_population"] == 29432
