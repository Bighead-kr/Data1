import pandas as pd

REQUIRED_COLUMNS = {
    "ltc_facilities_general.csv": [
        "장기요양기관코드", "시도 시군구 법정동명",
    ],
    "ltc_facilities_capacity.csv": [
        "장기요양기관코드", "기관유형코드", "정원",
    ],
    "region_codes_raw.csv": ["code", "name"],
}


def load_and_validate(path: str, required_columns: list[str]) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str)
    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        raise ValueError(f"missing required columns: {missing}")
    return df
