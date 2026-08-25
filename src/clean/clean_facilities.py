import pandas as pd
from src.clean.region_mapper import combine_region_key

INSTITUTIONAL_TYPE_CODES = {"A01", "A02", "A03", "A04", "A05", "AAA"}

def extract_sido_sigungu(full_name: str) -> tuple[str, str]:
    # 일부 실데이터 행은 주소 필드가 결측(NaN)이거나 토큰이 1개뿐이다.
    # 그런 행은 region_lookup에서 매칭되지 않도록 빈 문자열을 반환해
    # 기존 dropna(subset=["region_code"]) 로직으로 자연스럽게 걸러지게 한다.
    tokens = str(full_name).split()
    if len(tokens) < 2:
        return "", ""
    return tokens[0], tokens[1]

def clean_facilities(
    general_df: pd.DataFrame, capacity_df: pd.DataFrame, region_lookup: dict
) -> pd.DataFrame:
    general = general_df.drop_duplicates(subset=["장기요양기관코드"]).copy()
    general[["sido", "sigungu"]] = general["시도 시군구 법정동명"].apply(
        lambda s: pd.Series(extract_sido_sigungu(s))
    )
    general["region_code"] = general.apply(
        lambda r: region_lookup.get(combine_region_key(r["sido"], r["sigungu"])), axis=1
    )

    institutional = capacity_df[capacity_df["기관유형코드"].isin(INSTITUTIONAL_TYPE_CODES)].copy()
    institutional["정원"] = institutional["정원"].astype(float).astype(int)

    merged = institutional.merge(
        general[["장기요양기관코드", "region_code"]], on="장기요양기관코드", how="left"
    )
    merged = merged.dropna(subset=["region_code"])

    grouped = merged.groupby("region_code")["정원"].sum().reset_index()
    return grouped.rename(columns={"정원": "capacity"})
