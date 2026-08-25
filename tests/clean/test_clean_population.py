import pandas as pd
from src.clean.clean_population import clean_population

def test_clean_population_drops_summary_rows_and_maps_region_code():
    raw_df = pd.DataFrame(
        {
            "행정구역별(1)": ["행정구역별(1)", "전국", "서울특별시", "서울특별시", "세종특별자치시"],
            "행정구역별(2)": ["행정구역별(2)", "소계", "소계", "종로구", "소계"],
            "행정구역별(3)": ["행정구역별(3)", "소계", "소계", "소계", "소계"],
            "2025.1": ["65세이상인구 (명)", "10722557", "1881288", "29432", "50000"],
        }
    )
    region_lookup = {"서울특별시종로구": "11010", "세종특별자치시세종특별자치시": "36110"}

    result = clean_population(raw_df, region_lookup)

    assert set(result["region_code"]) == {"11010", "36110"}
    row = result[result["region_code"] == "11010"].iloc[0]
    assert row["elderly_population"] == 29432


def test_clean_population_resolves_jeonnam_gwangju_merged_entity_via_real_sido_names():
    # "전남광주통합특별시"는 행정구역별(1)에 등장하는 가상의 통합 명칭으로,
    # region_codes_raw.csv에는 존재하지 않는다. 실제 시도명은 행정구역별(2)에
    # (광주광역시/전라남도), 실제 시군구명은 행정구역별(3)에 들어있는 3단계 구조다.
    raw_df = pd.DataFrame(
        {
            "행정구역별(1)": [
                "행정구역별(1)",
                "전남광주통합특별시",
                "전남광주통합특별시",
                "전남광주통합특별시",
                "전남광주통합특별시",
                "전남광주통합특별시",
            ],
            "행정구역별(2)": ["행정구역별(2)", "소계", "광주광역시", "광주광역시", "전라남도", "전라남도"],
            "행정구역별(3)": ["행정구역별(3)", "소계", "소계", "동구", "소계", "목포시"],
            "2025.1": ["65세이상인구 (명)", "NaN", "265482", "26504", "486319", "47716"],
        }
    )
    region_lookup = {
        "광주광역시동구": "29010",
        "전라남도목포시": "36110",
    }

    result = clean_population(raw_df, region_lookup)

    assert set(result["region_code"]) == {"29010", "36110"}
    row = result[result["region_code"] == "29010"].iloc[0]
    assert row["elderly_population"] == 26504
    row = result[result["region_code"] == "36110"].iloc[0]
    assert row["elderly_population"] == 47716
