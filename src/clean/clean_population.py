import pandas as pd
from src.clean.region_mapper import combine_region_key

def clean_population(raw_df: pd.DataFrame, region_lookup: dict) -> pd.DataFrame:
    df = raw_df.iloc[1:].copy()  # 1행은 헤더 잔재라 스킵

    # "전남광주통합특별시"는 행정구역별(1)에만 등장하는 가상의 통합 명칭으로
    # region_codes_raw.csv엔 존재하지 않는다. 이 시도명 아래에서는 행정구역별(2)에
    # 실제 시도명(광주광역시/전라남도), 행정구역별(3)에 실제 시군구명이 들어있는
    # 3단계 구조를 쓴다. 그 외 모든 시도는 행정구역별(1)=시도, 행정구역별(2)=시군구인
    # 2단계 구조(행정구역별(3)은 항상 "소계"로 미사용).
    is_jeonnam_gwangju = df["행정구역별(1)"] == "전남광주통합특별시"

    df = df[
        (is_jeonnam_gwangju & (df["행정구역별(3)"] != "소계"))
        | (~is_jeonnam_gwangju & ((df["행정구역별(2)"] != "소계") | (df["행정구역별(1)"] == "세종특별자치시")))
    ].copy()

    def resolve_sido_sigungu(r):
        if r["행정구역별(1)"] == "전남광주통합특별시":
            return r["행정구역별(2)"], r["행정구역별(3)"]
        if r["행정구역별(1)"] == "세종특별자치시":
            return r["행정구역별(1)"], r["행정구역별(1)"]
        return r["행정구역별(1)"], r["행정구역별(2)"]

    df["region_code"] = df.apply(
        lambda r: region_lookup.get(combine_region_key(*resolve_sido_sigungu(r))), axis=1
    )
    df = df.dropna(subset=["region_code"])
    df["elderly_population"] = df["2025.1"].astype(int)
    return df[["region_code", "elderly_population"]].reset_index(drop=True)
