import pandas as pd
from src.clean.region_mapper import combine_region_key

def clean_population(raw_df: pd.DataFrame, region_lookup: dict) -> pd.DataFrame:
    df = raw_df.iloc[1:].copy()  # 1행은 헤더 잔재라 스킵
    df = df[
        (df["행정구역별(2)"] != "소계") | (df["행정구역별(1)"] == "세종특별자치시")
    ].copy()
    df["sigungu"] = df.apply(
        lambda r: r["행정구역별(1)"] if r["행정구역별(1)"] == "세종특별자치시" else r["행정구역별(2)"],
        axis=1,
    )
    df["region_code"] = df.apply(
        lambda r: region_lookup.get(combine_region_key(r["행정구역별(1)"], r["sigungu"])), axis=1
    )
    df = df.dropna(subset=["region_code"])
    df["elderly_population"] = df["2025.1"].astype(int)
    return df[["region_code", "elderly_population"]].reset_index(drop=True)
