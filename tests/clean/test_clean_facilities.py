import pandas as pd
from src.clean.clean_facilities import extract_sido_sigungu, clean_facilities

def test_extract_sido_sigungu_takes_first_two_tokens():
    assert extract_sido_sigungu("서울특별시 종로구 구기동") == ("서울특별시", "종로구")

def test_clean_facilities_filters_non_institutional_types_and_sums_capacity():
    general_df = pd.DataFrame(
        {
            "장기요양기관코드": ["F1", "F1", "F2"],
            "시도 시군구 법정동명": [
                "서울특별시 종로구 구기동",
                "서울특별시 종로구 구기동",
                "서울특별시 종로구 평창동",
            ],
        }
    ).drop_duplicates(subset=["장기요양기관코드"])
    capacity_df = pd.DataFrame(
        {
            "장기요양기관코드": ["F1", "F2", "F2"],
            "기관유형코드": ["A03", "A03", "B01"],
            "정원": [30, 20, 999],
        }
    )
    region_lookup = {"서울특별시종로구": "11010"}

    result = clean_facilities(general_df, capacity_df, region_lookup)
    row = result[result["region_code"] == "11010"].iloc[0]

    assert row["capacity"] == 50  # B01(재가서비스) 999는 제외되어야 함
